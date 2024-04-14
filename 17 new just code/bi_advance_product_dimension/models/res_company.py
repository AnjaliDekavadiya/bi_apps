# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models,fields

class res_partner(models.Model):
    _inherit = "res.company"
    
    price_calculation = fields.Selection([
        ('dimension', 'Price Calculation based on Dimension(m2/m3)'),
        ('qty', 'Price Calculation based on Qty'),
    ], string='Calculate Unit Price based on Height/Width', default='dimension')
