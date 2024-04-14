from odoo import models, fields, api, _


class KsMailMessage(models.Model):
    _name = 'ks.office.mail.job'
    _order = "create_date desc"
    _description = "Office 365 Mails Module Jobs Processes"
    _rec_name = "id"

    ks_inbox_records = fields.Integer(string="Inbox mail Processed", default=0)
    ks_sentbox_records = fields.Integer(string="Sent mail Processed", default=0)
    ks_archive_records = fields.Integer(string="Archive mail Processed", default=0)
    ks_mail_status = fields.Selection([('in_process', 'In Process'), ('completed', 'Completed'), ('error', 'Error')],
                                      string="Status")
    ks_mail_error_text = fields.Text("Error Message")
    ks_mail_job = fields.Selection([('calendar_import', 'Office to Odoo'), ('calendar_export', 'Odoo to Office'),
                                    ('contact_import', 'Office to Odoo'), ('contact_export', 'Odoo to Office'),
                                    ('mail_import', 'Office to Odoo'), ('mail_export', 'Odoo to Office'),
                                    ('task_import', 'Office to Odoo'), ('task_export', 'Odoo to Office')],
                                   string="Operation")
    ks_mail_module = fields.Selection(
        [('calendar', 'Calendar'), ('contact', 'Contact'), ('mail', 'Mail'), ('task', 'Task')],
        string="Module")
