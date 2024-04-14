# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _

    
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    sig_flag = fields.Boolean(string='Print Report')
    so_signature = fields.Binary(string='Signature')        
        
        
        
