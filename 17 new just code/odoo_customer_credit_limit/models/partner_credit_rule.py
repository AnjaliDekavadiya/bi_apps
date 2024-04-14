# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PartnerCreditRule(models.Model):
    _name = 'partner.credit.rule'
    
    @api.onchange('credit_type')
    def _onchange_credit_days(self):
        if self.credit_type == 'days':
            self.credit_days = 10
        else:
            self.credit_days = 0
            
    name = fields.Char(
        string='Name',
        required=True,
    )
    categ_ids = fields.Many2many(
        'product.category',
        string='Product Categories',
    )
    product_tmpl_ids = fields.Many2many(
        'product.template',
        string='Products',
    )
    credit_limit = fields.Float(
        'Credit Limits',
        required=True,
    )
    credit_type = fields.Selection(
        selection=[
            ('customer','Receivable Amount of Customer'),
            ('days','Due Amount Till Days'),
        ],
        string='Credit Limit Formula',
        default='customer'
    )
    credit_days = fields.Integer(
        string='Days',
#        default=_credit_days,
#        default=lambda self: '10' if self.credit_type == 'days' else '',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id
#        required=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )
