# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
from requests.structures import CaseInsensitiveDict
import random
import string
from dateutil.relativedelta import relativedelta
import paramiko
import logging
import os
import re
import time

_logger = logging.getLogger(__name__)


class DxSaasDbFilterOdooVersions(models.Model):
    _name = "dx.saas.dbfilter.odoo.versions"
    _description = "SAAS Odoo Versions"
    _rec_name = "odoo_version"

    odoo_version = fields.Float(string="Odoo Version", required=True, digits=(2, 1))


class DxSaasDbFilterServers(models.Model):
    _name = "dx.saas.dbfilter.servers"
    _description = "SAAS Server"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(string="Name", required=True, tracking=True)
    url = fields.Char(string="Odoo URL", required=True, tracking=True)
    ssh_username = fields.Char(string="SSH Username", required=True, tracking=True)
    ssh_password = fields.Char(string="SSH Password", required=True)
    master_password = fields.Char(string="Master Password", required=True)
    ssh_port = fields.Integer(string="SSH Port", required=True, default="22", tracking=True)
    http_port = fields.Integer(string="Odoo Local HTTP Port", required=True, default="8069", tracking=True)
    public_http_port = fields.Integer(string="Odoo Public HTTP Port", required=True, default="80", tracking=True)
    long_polling_port = fields.Integer(string="Long Polling Port", required=True, default="8072", tracking=True)
    create_db_path = fields.Char(string="Create DB Link", default="/web/database/create", tracking=True, required=True)
    drop_db_path = fields.Char(string="Create DB Link", default="/web/database/drop", tracking=True, required=True)
    backup_db_path = fields.Char(string="Backup DB Link", default="/web/database/backup", tracking=True, required=True)
    restore_db_path = fields.Char(string="Restore DB Link", default="/web/database/restore", tracking=True,
                                  required=True)
    odoo_version_id = fields.Many2one("dx.saas.dbfilter.odoo.versions", string="Odoo Version", required=False)
    odoo_variant = fields.Selection([
        ("community", "Community"),
        ("enterprise", "Enterprise"),
    ])
    custom_routes = fields.Boolean(string="Custom Database Manager Routes")
    subscriptions_count = fields.Integer(compute='_compute_subscriptions_count')
    active_subscriptions_count = fields.Integer(compute='_compute_active_subscriptions_count')
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirm", "Confirmed"),
    ], tracking=True)
    url_protocol = fields.Selection([
        ("http://", "http://"),
        ("https://", "https://")
    ], required=True, default="http://")
    custom_nginx_dirs = fields.Boolean(string="Custom nginx directories", default=False)
    nginx_available_dir = fields.Char(string="Nginx Available Dir", default="/etc/nginx/sites-available/",
                                      tracking=True,
                                      required=True)
    nginx_enabled_dir = fields.Char(string="Nginx Enabled Dir", default="/etc/nginx/sites-enabled/", tracking=True,
                                    required=True)
    nginx_root_dir = fields.Char(string="Nginx Root Dir", default="/var/www/html/", tracking=True,
                                 required=True)
    restart_nginx_cmd = fields.Char(string="Restart Nginx Command", default="service nginx restart", tracking=True,
                                    required=True)
    country_id = fields.Many2one('res.country', string='Country', tracking=True)
    state_id = fields.Many2one('res.country.state', string='States', domain="[('country_id', '=?', country_id)]",
                               tracking=True)
    domain_for_new_sub = fields.Char(string="Main Domain", required=True, tracking=True)

    @api.onchange("url_protocol")
    def url_protocol_onchange(self):
        if self.url_protocol == "http://":
            self.public_http_port = 80
        else:
            self.public_http_port = 443

    @api.model
    def create(self, vals):
        res = super(DxSaasDbFilterServers, self).create(vals)
        if res["url"].startswith("http://") or res["url"].startswith("http://"):
            raise UserError(_("Please remove http:// or https:// Server %s URL") % res["name"])
        res["state"] = "draft"

        return res

    def unlink(self):
        for server in self:
            if server.state != "draft" and server.active_subscriptions_count != 0:
                raise UserError(_("Server %s can not be deleted because it have active subscriptions") % server.name)
        return super(DxSaasDbFilterServers, self).unlink()

    def _compute_subscriptions_count(self):
        for record in self:
            record.subscriptions_count = self.env["dx.saas.dbfilter.subscriptions"].search_count(
                [('server_id', '=', self.id)])

    def get_subscriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Subscriptions',
            'view_mode': 'tree',
            'res_model': 'dx.saas.dbfilter.subscriptions',
            'domain': [('server_id', '=', self.id)],
            'context': "{'create': False, 'delete': False}"
        }

    def _compute_active_subscriptions_count(self):
        for record in self:
            record.active_subscriptions_count = self.env["dx.saas.dbfilter.subscriptions"].search_count(
                [('server_id', '=', self.id), ('state', 'not in', ["draft", "cancel"])])

    def get_active_subscriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Active Subscriptions',
            'view_mode': 'tree',
            'res_model': 'dx.saas.dbfilter.subscriptions',
            'domain': [('server_id', '=', self.id), ('state', 'not in', ["draft", "cancel"])],
            'context': "{'create': False, 'delete': False}"
        }

    def action_confirm(self):
        if self.state != "draft":
            return
        return self.write({"state": "confirm"})

    def reset_to_draft(self):
        for server in self:
            if server.active_subscriptions_count != 0:
                raise UserError(_("Server %s have active subscriptions and can not reset to draft") % server.name)
            else:
                return server.write({"state": "draft"})


class DxSaasDbFilterSubscriptions(models.Model):
    _name = "dx.saas.dbfilter.subscriptions"
    _description = "SAAS Subscription"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", tracking=True, readonly=True)
    client_id = fields.Many2one("res.partner", string="Client", required=True, tracking=True)
    server_id = fields.Many2one("dx.saas.dbfilter.servers", string="Server", required=True, tracking=True,
                                domain="[('state', '=', 'confirm')]")
    start_date = fields.Date(string="Start date", required=True, tracking=True)
    end_date = fields.Date(string="End date", required=False, tracking=True)
    active = fields.Boolean(string="Active", default=True)
    domain = fields.Char(string="Domain", required=True, tracking=True)
    login = fields.Char(string="Login", required=False, tracking=True, readonly=True)
    password = fields.Char(string="Password", readonly=True, required=False)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirm", "Confirmed"),
        ("running", "Running"),
        ("stopped", "Stopped"),
        ("cancel", "Canceled"),
    ], tracking=True)
    use_ssl = fields.Boolean(string="Create SSL Cretification", default=False)
    users_count = fields.Integer(string="Users Count", required=True, default=1, tracking=True)
    packages_id = fields.Many2many("dx.saas.packages", string="Packages", required=True)
    error_creating_nginx = fields.Boolean(string="Error Creating Nginx Files", default=False)
    error_installing_modules = fields.Boolean(string="Error Installing SUbscription Modules", default=False)
    error_creating_db = fields.Boolean(string="Error Creating Database", default=False)

    _sql_constraints = [
        ('field_unique', 'unique(domain)', 'Subscription "DOMAIN" Must be unique!'),
    ]

    @api.onchange('domain')
    def domain_onchange(self):
        pattern = re.compile("^[a-zA-Z0-9][a-zA-Z0-9_.-]+$")
        if self.domain:
            if not pattern.match(self.domain):
                raise ValidationError(_('Domain is not valid'))

    @api.model
    def create(self, vals):
        res = super(DxSaasDbFilterSubscriptions, self).create(vals)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        res["name"] = "Draft"
        res["state"] = "draft"
        res["login"] = res['client_id'].email or "admin"
        res["password"] = ran
        return res

    cwd = os.path.dirname(__file__)
    templates_folder = cwd + "/templates/"
    tmp_dir = "/tmp/"

    def unlink(self):
        for subscription in self:
            if subscription.state not in ["draft", "cancel"]:
                raise UserError(
                    _("You cannot delete subscription %s which is not draft or cancelled") % subscription.name)
        return super(DxSaasDbFilterSubscriptions, self).unlink()

    def action_send_saas_details_email(self, from_code=False):
        self.ensure_one()
        try:
            ir_model_data = self.env['ir.model.data']
            template_id_record = ir_model_data._xmlid_lookup('dx_saas_dbfilter.dx_dbfilter_new_sub_email_template')
            template_id = template_id_record[1]
            if from_code:
                self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
                return True
        except ValueError:
            template_id = False

        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False

        ctx = {
            **self.env.context,
            'default_model': 'dx.saas.dbfilter.subscriptions',
            'default_res_ids': self.ids,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'force_email': True,
        }

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id.id, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def ssh_sftp(self, files=[], commands=[], rm_commands=[]):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.server_id.url, self.server_id.ssh_port,
                        self.server_id.ssh_username,
                        self.server_id.ssh_password)
            if rm_commands:
                for cmd in rm_commands:
                    ssh.exec_command(cmd)
                    _logger.info(_("Command for subscription %s executed successfully" % self.name))
            if files:
                sftp = ssh.open_sftp()
                for file in files:
                    sftp.put(file["file"], file["destination"])
                sftp.close()
            _logger.info(_("File for subscription %s uploaded to server" % self.name))
            if commands:
                for cmd in commands:
                    ssh.exec_command(cmd)
                    if 'acme.sh' in cmd:
                        time.sleep(35)
                    _logger.info(_("Command for subscription %s executed successfully" % self.name))
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            _logger.error(
                _("Authentication failed to server %s, please verify your credentials" % self.server_id.name))
            return False
        except paramiko.SSHException as sshException:
            _logger.error(_("Unable to stablish ssh connection to server %s error is %s" % (
                self.server_id.name, sshException)))
            return False

    def nginx_action(self, action='create'):
        # action (create, stop, start, remove)
        remote_nginx_available_dir = self.server_id.nginx_available_dir
        remote_nginx_enabled_dir = self.server_id.nginx_enabled_dir
        remote_nginx_root_dir = self.server_id.nginx_root_dir
        restart_nginx = self.server_id.restart_nginx_cmd
        file_name = self.domain + ".nginx"
        file_dest = self.tmp_dir + file_name
        files = []
        commands = []
        rm_commands = []
        if action == "create" or action == "start":
            if self.use_ssl:
                if action == "create":
                    commands.append("/root/.acme.sh/acme.sh --issue -d %s -w /var/www/html" % self.domain)
                file_source = self.templates_folder + "nginx_config_template"
            else:
                file_source = self.templates_folder + "nginx_config_no_ssl_template"
            fin = open(file_source, "rt")
            fout = open(file_dest, "wt")
            web_socket = self.server_id.odoo_version_id.odoo_version > 15.0 and '/websocket' or '/longpolling'
            for line in fin:
                fout.write(line.replace("_SERVER_NAME_", self.domain).replace("_HTTP_PORT_",
                                                                              str(self.server_id.http_port)).replace(
                    "_LONG_PORT_", str(self.server_id.long_polling_port)).replace("_WEBSOCKET_", str(web_socket)))
            fin.close()
            fout.close()
            if action == "start":
                # Remove old configs
                rm_commands.append("rm %s%s %s%s" % (remote_nginx_available_dir, file_name,
                                                     remote_nginx_enabled_dir, file_name))
            commands.append("ln -s %s%s %s" % (remote_nginx_available_dir, file_name, remote_nginx_enabled_dir))
            commands.append(restart_nginx)
            files.append({
                "file": file_dest,
                "destination": remote_nginx_available_dir + file_name
            })
        if action == "stop":
            # Upload ended subscription file
            files.append({
                "file": self.templates_folder + "subscription_ended.html",
                "destination": remote_nginx_root_dir + "subscription_ended.html"
            })
            if self.use_ssl:
                file_source = self.templates_folder + "nginx_config_expiration_template"
            else:
                file_source = self.templates_folder + "nginx_config_no_ssl_expiration_template"
            fin = open(file_source, "rt")
            fout = open(file_dest, "wt")
            for line in fin:
                fout.write(line.replace("_SERVER_NAME_", self.domain).replace("_ROOT_DIR_",
                                                                              remote_nginx_root_dir))
            fin.close()
            fout.close()
            # Remove old configs
            rm_commands.append("rm %s%s %s%s" % (remote_nginx_available_dir, file_name,
                                                 remote_nginx_enabled_dir, file_name))
            commands.append("ln -s %s%s %s" % (remote_nginx_available_dir, file_name,
                                               remote_nginx_enabled_dir))
            commands.append(restart_nginx)
            file = {
                "file": file_dest,
                "destination": remote_nginx_available_dir + file_name
            }
            files.append(file)
        if action == "remove":
            rm_commands.append("rm %s%s %s%s" % (remote_nginx_available_dir, file_name,
                                                 remote_nginx_enabled_dir, file_name))
            commands.append(restart_nginx)
            # self.ssh_sftp(False, commands)

        go = self.ssh_sftp(files, commands, rm_commands)
        if go:
            return self.write({"error_creating_nginx": False})
        else:
            self.message_post(body=_("Could not create nginx configs please see logs for extra info and recreate it"))
            return self.write({"error_creating_nginx": True})

    def action_confirm(self):
        if self.state != "draft":
            return
        name = self.env["ir.sequence"].next_by_code("dx.saas.subscription")
        return self.write({"state": "confirm", "name": name})

    def install_subscription_modules(self):
        try:
            headers = {'content-type': 'application/json'}
            protocol = self.use_ssl and 'https://' or 'http://'
            modules_url = protocol + self.domain + "/dx_install_modules"
            modules = []
            for package in self.packages_id:
                for module in package.modules_id:
                    modules.append(module.technical_name)
            modules = list(dict.fromkeys(modules))
            modules_body = json.dumps({
                "jsonrpc": "2.0",
                "params": {
                    "modules": modules,
                }
            })
            modules_req = requests.post(modules_url, headers=headers, data=modules_body, timeout=240,
                                        allow_redirects=False)
            if modules_req.status_code == 200:
                if modules_req.json().get("result"):
                    if modules_req.json()["result"]["status"] == "success":
                        self.message_post(body=
                                          _("Subscription Modules Installed Successfully"))
                        return self.write({"error_installing_modules": False})
                    else:
                        self.message_post(body=
                                          _("Error in installing subscription modules error is %s" %
                                            modules_req.json()["result"][
                                                "message"]))
                        return self.write({"error_installing_modules": True})

            else:
                self.error_installing_modules = True
                self.message_post(body=_("Error installing subscription modules - %s" % modules_req.status_code))
                return True
        except requests.exceptions.Timeout:
            self.message_post(body=_("Error installing subscription modules - Time out error"))
            return self.write({"error_installing_modules": True})
        except requests.exceptions.RequestException as e:
            self.message_post(body=_("Error installing subscription modules - %s" % e))
            return self.write({"error_installing_modules": True})

    def action_create_client_db(self):
        url = self.server_id.url_protocol + self.server_id.url + ":" + str(self.server_id.public_http_port) + \
              self.server_id.create_db_path
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = "master_pwd=%s&name=%s&login=%s&password=%s&lang=en_US&phone=&country_code=" % (
            self.server_id.master_password, self.domain, self.login, self.password)
        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code == 200:
            self.nginx_action("create")
            self.action_send_saas_details_email(from_code=True)
            self.install_subscription_modules()
            self.write({"error_creating_db": False})
            return self.write({"state": "running"})
        else:
            return self.write({"error_creating_db": True})

    def action_stop_client_db(self):
        if self.state != "running":
            return
        self.nginx_action("stop")
        return self.write({"state": "stopped"})

    def action_start_client_db(self):
        if self.state != "stopped":
            return
        self.nginx_action("start")

        return self.write({"state": "running"})

    def action_cancel(self):
        if self.state in ["draft", "confirm"]:
            return self.write({"state": "cancel"})

        url = self.server_id.url_protocol + self.server_id.url + ":" + str(self.server_id.public_http_port) + \
              self.server_id.drop_db_path
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = "master_pwd=%s&name=%s" % (self.server_id.master_password, self.domain)
        resp = requests.post(url, headers=headers, data=data)

        if resp.status_code == 200:
            self.write({"state": "cancel"})
        self.nginx_action("remove")

    @api.model
    def cron_stop_saas_ended_subscriptions(self, grace_period):
        grace_period_config = int(
            self.env["ir.config_parameter"].sudo().get_param("dx_saas_dbfilter.grace_period", "False"))
        g_period = grace_period_config or grace_period or 0
        ended_subscriptions = self.env["dx.saas.dbfilter.subscriptions"].search([
            ("end_date", "<", fields.Date.context_today(self) + relativedelta(days=g_period)),
            ("state", "=", "running")
        ])
        for end in ended_subscriptions:
            self.nginx_action("stop")
            end.state = "stopped"


class DxModulesModules(models.Model):
    _name = "dx.saas.modules"
    _description = "Modules"
    _rec_name = "technical_name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    technical_name = fields.Char(string="Module Technical Name", required=True, tracking=True)
    description = fields.Char(string="Description", required=False)

    _sql_constraints = [
        ('field_unique',
         'unique(technical_name)',
         'Module "NAME" Must be unique!')
    ]


class DxModulesPackages(models.Model):
    _name = "dx.saas.packages"
    _description = "Packages"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True)
    modules_id = fields.Many2many("dx.saas.modules", string="Modules")

    _sql_constraints = [
        ('field_unique',
         'unique(name)',
         'Package "NAME" Must be unique!')
    ]
