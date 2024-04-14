# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _

    
class account_invoice(models.Model):
    _inherit = 'account.move'
    
    sig_flag = fields.Boolean(string='Print Report')
    so_signature = fields.Binary(string='Signature')        
    
    
    
        
        

    
