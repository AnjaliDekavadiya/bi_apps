# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models,api,_
from odoo.exceptions import ValidationError

class courier_weight_rule(models.Model):
    _name = 'dev.courier.weight.rule'
    _description = 'Courier Weight Rule'
    _order = "name"

    name = fields.Char('Name')
    from_weight = fields.Float('From Weight')
    to_weight = fields.Float('To Weight')
    price = fields.Monetary('Price')
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    
    @api.constrains('from_weight','to_weight')  
    def check_weight_from_to(self):
        for rule in self:
            if rule.from_weight > rule.to_weight:
                raise ValidationError(_('From Weight must be less of To Weight'))
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
