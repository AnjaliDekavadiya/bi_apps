# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountInvoice(models.Model):
#    _inherit = 'account.invoice' odoo13
    _inherit = 'account.move'
    
    rma_order_id = fields.Many2one(
        'return.order',
        string = "RMA Order"
    )
