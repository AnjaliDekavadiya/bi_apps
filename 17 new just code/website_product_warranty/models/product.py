# -*- coding: utf-8 -*-
# from openerp import fields, models, api, _
from odoo import fields, models, api, _


class product_template(models.Model):
    _inherit = 'product.template'
    
    custom_show_product_warranty = fields.Boolean('Display Website Warranty', help="Tick this box if you want to display product warranty information on website shop.")
    custom_product_warranty = fields.Integer('Warranty Description', help="Content of this description will be visible on website shop.")
    custom_website_policies = fields.Text('Website Policies', default='30-day money-back guarantee \nFree Shipping in U.S. Buy now,\nget in 2 days')
    custom_warranty_type = fields.Selection(
        [('day','- Days'),
         ('week','- Weeks'),
         ('month','- Month'),
         ('year','- Year')],
        string='Warranty Type',
        default = 'day',
    )
