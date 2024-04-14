from odoo import models, fields, api


class Office365MailCategory(models.Model):
    _name = 'mail.category'
    _rec_name = 'name'
    _description = "Outlook Categories for Syncing Mails"

    name = fields.Char(string="Mail Category")