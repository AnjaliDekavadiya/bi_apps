# coding: utf-8

from odoo import fields, models, api , _


class CashOnDeliveryCollection(models.Model):
    _name = 'cashondelivery.collection'
    _description = 'Cash on Delivery Collection'
    _rec_name = 'saleorder_id'

    # @api.multi #odoo13
    @api.depends('saleorder_id', 'saleorder_id.transaction_ids')
    def _compute_transaction_id(self):
        for record in self:
            if record.saleorder_id and record.saleorder_id.transaction_ids:
                transaction_ids = record.saleorder_id.transaction_ids
                record.transaction_id = transaction_ids.sorted(lambda i: i.id, reverse=True)[0]

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Canceled')],
        default='draft',
        tracking=True,
    )
    saleorder_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
    )
    transaction_id = fields.Many2one(
        'payment.transaction',
        string='Payment Transaction',
        compute="_compute_transaction_id",
#         related="saleorder_id.payment_tx_id",
        store=True,
        readonly=True
    )
    amount_order = fields.Monetary(
        string='Order Amount',
        related="saleorder_id.amount_total",
    )
    collection_amount = fields.Float(
        string='Collection Amount',
        required=True,
    )
    delivery_boy_id = fields.Many2one(
        'res.partner',
        string='Delivery Company / Person',
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='saleorder_id.partner_id',
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='saleorder_id.company_id',
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='saleorder_id.currency_id',
        store=True,
    )
    description = fields.Text(
        string='Internal Notes',
    )

    # @api.multi #odoo13
    def set_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    # @api.multi #odoo13
    def set_done(self):
        for rec in self:
            rec.state = 'done'
            
    # @api.multi #odoo13
    def set_cancel(self):
        for rec in self:
            rec.state = 'cancel'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
