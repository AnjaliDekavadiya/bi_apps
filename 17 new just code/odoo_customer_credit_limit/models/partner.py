# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    @api.onchange('credit_rule_id')
    def _onchange_credit_rule_id(self):
        self.credit_limit = self.credit_rule_id.credit_limit
    
    credit_rule_id = fields.Many2one(
        'partner.credit.rule',
        string='Credit Limit Rule',
    )
