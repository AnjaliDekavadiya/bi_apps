# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class IrMailServer(models.AbstractModel):
    _inherit = "ir.mail_server"

    smtp_user = fields.Char(string='Username', help="Optional username for SMTP authentication", groups='is_mail_inbox.group_mail_box_config_user')
    smtp_pass = fields.Char(string='Password', help="Optional password for SMTP authentication", groups='is_mail_inbox.group_mail_box_config_user')
    smtp_ssl_certificate = fields.Binary(
        'SSL Certificate', groups='is_mail_inbox.group_mail_box_config_user', attachment=False,
        help='SSL certificate used for authentication')
    smtp_ssl_private_key = fields.Binary(
        'SSL Private Key', groups='is_mail_inbox.group_mail_box_config_user', attachment=False,
        help='SSL private key used for authentication')
