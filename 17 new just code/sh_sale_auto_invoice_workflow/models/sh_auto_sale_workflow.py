from odoo import fields, models


class AutoSaleWorkflow(models.Model):
    _name = 'sh.auto.sale.workflow'
    _description = "Auto Sale Workflow"

    name = fields.Char(string="Name", required=True)
    validate_order = fields.Boolean(string="Delivery Order")
    create_invoice = fields.Boolean(string="Create Invoice")
    validate_invoice = fields.Boolean(string="Validate Invoice")
    register_payment = fields.Boolean(string="Register Payment")
    send_invoice_by_email = fields.Boolean(string="Send Invoice By Email")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company, store=True)
    sale_journal = fields.Many2one(
        'account.journal', string="Sale Journal", domain="[('company_id', '=', company_id)]")
    payment_journal = fields.Many2one(
        'account.journal', string="Payment Journal", domain="[('company_id', '=', company_id)]")
    payment_method = fields.Many2one(
        'account.payment.method', string="Payment Method")
    force_transfer = fields.Boolean(string="Force Transfer")
