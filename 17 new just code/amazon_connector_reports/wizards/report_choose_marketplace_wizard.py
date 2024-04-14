from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportChooseMarketplaceWizard(models.TransientModel):
    _name = "report.choose.marketplace.wizard"

    marketplace_ids = fields.Many2many(
        'amazon.marketplace',
        string="Marketplaces",
        # domain="[('id', 'in', active_marketplace_ids)]",
    )
    processing_type = fields.Selection(
        [
            ("normal", "Normal Processing (Needs feature implementation)"),
            ("spreadsheet", "Create Spreadsheet"),
            ("record", "Create Record Lines")
        ],
        default="normal",
        string="Processing Type",
        required=True,
    )

    def report_generate_cron(self):
        report_type_id = self.env.context.get("active_id")
        report_type = self.env["amazon.report.type"].browse(report_type_id)
        report_type.generate_auto_retrieve_process_report(
            marketplaces=self.marketplace_ids, processing_type=self.processing_type)

