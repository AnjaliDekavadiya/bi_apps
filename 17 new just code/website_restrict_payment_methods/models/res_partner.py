# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    custom_payment_acquirer_ids = fields.Many2many(
#        'payment.acquirer', 
        'payment.provider', 
        string='Payment Acquirers',
        copy=True
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
