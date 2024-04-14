# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _

    
class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    sig_flag = fields.Boolean(string='Print Report')
    sp_signature = fields.Binary(string='Signature')  
    sp_user_id = fields.Many2one('res.users', string='user',default=lambda self: self.env.user)      
        
        

    
