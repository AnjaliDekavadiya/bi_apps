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

class courier_distance_rule(models.Model):
    _name = 'dev.courier.distance.rule'
    _description = 'Courier Distance Rule'
    _order = "name"

    name = fields.Char('Name')
    from_km = fields.Integer('From KM')
    to_km = fields.Integer('To KM')
    price = fields.Monetary('Price')
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company)
    
    @api.constrains('from_km','to_km')  
    def check_from_km_to_km(self):
        for rule in self:
            if not rule.from_km or not rule.to_km:
                raise ValidationError(_('Distance must be positive.'))
            if rule.from_km > rule.to_km:
                raise ValidationError(_('Distance From must be less of Distance To.'))
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
