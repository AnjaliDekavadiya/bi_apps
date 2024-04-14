# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _

    
class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    sig_flag = fields.Boolean(string='Print Report')
    po_signature = fields.Binary(string='Signature')  
    po_user_id = fields.Many2one('res.users', string='user',default=lambda self: self.env.user)      
        
        

