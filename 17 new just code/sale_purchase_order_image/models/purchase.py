# -*- coding: utf-8 -*-
# from openerp import fields, models, api
from odoo import fields, models, api
# 
# class purchase_config_settings(models.TransientModel):
#     _inherit = 'res.config.settings'
#     
#     print_line_number = fields.Boolean('Print Line Number')
#     print_product_image = fields.Boolean('Print Product Image')
# 
#     @api.model
#     def get_default_print_line_number(self, fields):
#         return {'print_line_number': self.env['ir.values'].get_default(
#                 'res.config.settings', 'print_line_number')}
#     
#     @api.model
#     def set_default_print_line_number(self):
#         config_value = self.print_line_number
#         self.env['ir.values'].set_default('purchase.config.settings', 'print_line_number', config_value)
# 
#     @api.model
#     def get_default_print_product_image(self, fields):
#         return {'print_product_image': self.env['ir.values'].get_default(
#                 'purchase.config.settings', 'print_product_image')}
# 
#     @api.model
#     def set_default_print_product_image(self):
#         config_value = self.print_product_image
#         self.env['ir.values'].set_default('purchase.config.settings', 'print_product_image', config_value)

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    @api.model
    def _get_print_line_number(self):
        #check if print_line_number is globally set then by default print_line_number is true
        #is_print_line_number_set = self.env['ir.values'].get_default('res.config.settings', 'print_line_number')
        is_print_line_number_set = self.env['ir.config_parameter'].sudo().get_param('sale_purchase_order_image.purchase_print_line_number') #odoo11
        if is_print_line_number_set:
            return True
        return False
    
    @api.model
    def _get_print_product_image(self):
        #check if print_product_image is globally set then by default print_product_image is true
#         is_print_product_image_set = self.env['ir.values'].get_default('res.config.settings', 'print_product_image')
        is_print_product_image_set = self.env['ir.config_parameter'].sudo().get_param('sale_purchase_order_image.purchase_print_product_image') #odoo11
        if is_print_product_image_set:
            return True
        return False

    print_line_number = fields.Boolean('Print Line Number', default=_get_print_line_number)
    print_product_image = fields.Boolean('Print Product Image', default=_get_print_product_image)

    @api.onchange('print_product_image', 'print_line_number')
    def on_change_print_product_image(self):
        for line in self.order_line:
            line.print_product_image = self.print_product_image
            line.print_line_number = self.print_line_number

    
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    print_line_number = fields.Boolean('Print Line Number')
    print_product_image = fields.Boolean('Print Product Image')
#     prouduct_small_image = fields.Binary(related='product_id.image_small', string='Image')
    product_small_image = fields.Binary(string='Image')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(purchase_order_line, self).onchange_product_id()
        # self.product_small_image =  self.product_id.image_medium
        # self.prouduct_small_image = self.product_id.image_1920
        self.product_small_image = self.product_id.image_1920
        return res
        
    # @api.model
    # def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        # res = super(purchase_order_line, self).create(vals)
        res = super(purchase_order_line, self).create(vals_list)
        if res.order_id.print_line_number:
            res.print_line_number = True
        if res.order_id.print_product_image:
            res.print_product_image = True
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: