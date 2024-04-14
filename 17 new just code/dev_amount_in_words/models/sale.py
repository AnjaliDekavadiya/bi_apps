# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api
from num2words import num2words
    
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    amount_display_flag = fields.Boolean("Print Amount in PDF")
    amount_in_words = fields.Char(compute='amount_word', string='Amount In Word', readonly=True)

    
    @api.depends('amount_in_words')
    def amount_word(self):
        for record in self:
            record.amount_in_words = num2words(record.amount_total) + ' Only'
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
