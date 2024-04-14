from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    fba_return_report_id = fields.Many2one(
        comodel_name="amazon.report.log",
        string="FBA Return Report",
    )
    return_date = fields.Datetime("Return Datetime")
    return_reason = fields.Char("Return Reason")
    customer_comment = fields.Char("Customer Comments")
    returned_condition = fields.Char("Condition")
    amz_return_status = fields.Char("Amazon Status")
    returned_to_fc = fields.Char("Returned to Fulfillment Center")
    license_plate_number = fields.Char("License Plate Number")
