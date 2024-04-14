# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Crm(models.Model):
    _inherit = 'crm.lead'
    
    sale_user_group_id = fields.Many2one(
        'sale.user.group',
        string='Sales Group',
    )
    
    @api.onchange('partner_id')
    def _onchange_custom_partner_id(self):
        self.sale_user_group_id = self.partner_id.sale_user_group_id.id
        # res = super(Crm, self)._onchange_partner_id()
        # return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
