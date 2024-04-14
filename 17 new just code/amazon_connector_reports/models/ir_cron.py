from odoo import fields, models


class IrCron(models.Model):
    _inherit = 'ir.cron'

    amazon_report_type_id = fields.Many2one("amazon.report.type", string="Report Type")

