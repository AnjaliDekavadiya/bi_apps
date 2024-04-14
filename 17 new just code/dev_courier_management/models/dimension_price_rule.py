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

class courier_dimension_rule(models.Model):
    _name = 'dev.courier.dimension.rule'
    _description = 'Courier Dimension Rule'
    _order = "name"

    name = fields.Char('Name')
    length = fields.Integer('Length')
    width = fields.Integer('Width')
    height = fields.Integer('Height')
    price = fields.Monetary('Price')
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)

    def name_get(self):
        return [(rec.id, ('%s X %s X %s' % (rec.length, rec.width, rec.height))) for rec in self]
    
    @api.constrains('length','width', 'height')  
    def check_length_width_height(self):
        for rule in self:
            if not rule.length or not rule.width or not rule.height:
                raise ValidationError(_('Length, Width and Height must be positive.'))
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
