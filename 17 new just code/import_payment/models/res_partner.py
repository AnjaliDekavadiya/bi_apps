# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'
    
    # @api.multi
    @api.depends()
    def _set_customer_code(self):
        for rec in self:
            rec.custom_customer_code = rec.id
    
    custom_customer_code = fields.Integer(
        compute='_set_customer_code',
        string='Customer Code',
        store=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
