# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pysftp
import ftplib


class FtpServer(models.Model):
    _name = "ftp.server"
    _description = "FTP Server"

    name = fields.Char("Server Name", required=True, copy=False, help="FTP Server Name.")
    host = fields.Char("Host", required=True, copy=False, help="FTP Server HOST IP / URL.")
    port = fields.Integer("Port", required=True, copy=False, default=22, help="FTP Server Connection Port.")
    username = fields.Char("Username", required=True, copy=False, help="FTP Server connection username.")
    password = fields.Char("Password", required=True, copy=False, help="FTP Server connection password.")
    state = fields.Selection([("draft", "Draft"),
                              ("confirmed", "Confirmed")],
                             "State", required=True, default="draft", copy=False, help="FTP Connection state.")
    ftp_connection_working_properly = fields.Boolean("FTP Connection Working Properly", default=False, copy=False,
                                                     help="Check true if ftp connection is working properly.")
    active = fields.Boolean("Active", default=True, copy=False, help="Check true, if record is active.")
    directory_ids = fields.One2many("ftp.directory", "ftp_server_id", "Directories", copy=False, help="FTP Server Directories.")
    company_id = fields.Many2one("res.company", required=True, copy=False, default=lambda self: self.env.company.id,
                                 help="Related Company")
    is_product_process = fields.Boolean("Product Export Process", default=True, copy=False,
                                        help="Do you want to process products for this FTP Server? ")
    is_sales_process = fields.Boolean("Sales Transfer Import/Export", default=True, copy=False,
                                      help="Do you want to process sales transfers for this FTP Server? ")
    is_sales_return_process = fields.Boolean("Sales Return Transfer Import/Export", default=True, copy=False,
                                             help="Do you want to process sales return transfers for this FTP Server? ")
    is_purchase_process = fields.Boolean("Purchase Import/Export", default=True, copy=False,
                                         help="Do you want to process purchase transfers for this FTP Server? ")
    is_stock_process = fields.Boolean("Stock Import Process", default=True, copy=False,
                                      help="Do you want to process stock imports for this FTP Server?")
    connection_type = fields.Selection([('sftp', 'SFTP'), ('ftp', 'FTP')], default='sftp', copy= False,
                                       help="Select Connection type.")

    def unlink(self):
        for unlink in self: 
            if unlink.state == 'confirmed':
                raise UserError(_("You Can't Delete The Instance In Confirmed State!!."))
            return super(FtpServer, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        for cpy in self: 
            if cpy.state == 'confirmed':
                raise UserError(_("You Can Not Duplicate This Instance!!."))
            return super(FtpServer, self).copy(default=None)

    def reset_to_draft(self):
        return self.write({"state": "draft",
                           "ftp_connection_working_properly": False})

    def confirm_instance(self):
        if not self.ftp_connection_working_properly:
            raise UserError(_("Test Connection First To Confirm FTP Server Credentials."))
        return self.write({"state": "confirmed"})

    def test_connection(self):
        try:
            self.connect_to_ftp_server()
            self.ftp_connection_working_properly = True
            self._cr.commit()
            return {
                'name': (_("Connection Successful")),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ftp.test.connection.wizard',
                'target':'new',
                'context':{'default_name':"Test connection is successful now\n,you can now confirm instance "} 
            }
        except Exception as e:
            raise UserError(_(e))

    def connect_to_ftp_server(self):
        try:
            if self.connection_type == 'sftp':
                connection = pysftp.Connection(host=self.host,
                                               port=self.port,
                                               username=self.username,
                                               password=self.password)
            else:
                connection = ftplib.FTP()
                connection.connect(self.host, self.port)
                connection.login(self.username, self.password)
        except Exception as e:
            raise UserError(_("Facing issue in connection process : %s" % e))
        return connection

    def check_update_path_directory(self, sftp_instance, dir_path):
        path_dir_list = dir_path.split("/")
        current_path = path_dir_list[0]
        for index in range(1, len(path_dir_list)-1):
            current_path = "%s/%s" % (current_path or "", path_dir_list[index] or "")
            if self.connection_type == 'sftp':
                if not sftp_instance.isdir(current_path):
                    sftp_instance.mkdir(current_path, mode=777)
            else:
                try:
                    sftp_instance.nlst(path_dir_list[index])
                except Exception as e:
                    sftp_instance.mkd(current_path)
                sftp_instance.cwd(current_path)

    def check_ftp_directory(self, sftp_instance, dir_path):
        try:
            sftp_instance.nlst(dir_path)
        except Exception as e:
            return True
        return False


class FtpDirectory(models.Model):
    _name = "ftp.directory"
    _description = "FTP Server Directories."

    name = fields.Char("Name", required=True, copy=False, help="Directory Name")
    path = fields.Char("Path", required=True, copy=False, help="Path of directory on FTP server.")
    ftp_server_id = fields.Many2one("ftp.server", "FTP Server", required=True, copy=False, help="Related FTP Server.")
    company_id = fields.Many2one("res.company", required=True, copy=False, default=lambda self: self.env.company.id,
                                 help="Related Company")
