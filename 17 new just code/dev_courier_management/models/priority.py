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

class courier_priority(models.Model):
    _name = 'dev.courier.priority'
    _description = 'Courier Priority'
    _order = "name"

    name = fields.Char('Name')
    price = fields.Monetary('Price', default=1)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
