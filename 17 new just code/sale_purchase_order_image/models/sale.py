# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #add the field in sale settings
    print_line_number = fields.Boolean('Print Line Number')
    print_product_image = fields.Boolean('Print Product Image')
    
    purchase_print_line_number = fields.Boolean('Purchase Print Line Number')
    purchase_print_product_image = fields.Boolean('Purchase Print Product Image')
#     @api.model
#     def get_default_print_line_number(self, fields):
#         return {'print_line_number': self.env['ir.values'].get_default(
#                 'res.config.settings', 'print_line_number')}
#     
#     @api.model
#     def set_default_print_line_number(self):
#         config_value = self.print_line_number
#         self.env['ir.values'].set_default('res.config.settings', 'print_line_number', config_value)
# 
#     @api.model
#     def get_default_print_product_image(self, fields):
#         return {'print_product_image': self.env['ir.values'].get_default(
#                 'res.config.settings', 'print_product_image')}
#     
#     @api.model
#     def set_default_print_product_image(self):
#         config_value = self.print_product_image
#         self.env['ir.values'].set_default('res.config.settings', 'print_product_image', config_value)
    
    
#     @api.multi
#     def set_commission_based_on_defaults(self):
#         if self.when_to_pay == 'invoice_payment':
#             if self.commission_based_on == 'product_category' or self.commission_based_on == 'product_template':
#                 raise UserError(_("Sales Commission: You can not have commision based on product or category if you have selected when to pay is payment."))
#         return self.env['ir.values'].sudo().set_default(
#             'sale.config.settings', 'commission_based_on', self.commission_based_on)
# 
#     @api.multi
#     def set_when_to_pay_defaults(self):
#         return self.env['ir.values'].sudo().set_default(
#             'sale.config.settings', 'when_to_pay', self.when_to_pay)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            print_line_number = params.get_param('sale_purchase_order_image.print_line_number'),
            print_product_image = params.get_param('sale_purchase_order_image.print_product_image'),
            purchase_print_line_number = params.get_param('sale_purchase_order_image.purchase_print_line_number'),
            purchase_print_product_image = params.get_param('sale_purchase_order_image.purchase_print_product_image')
        )
        return res

    # @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("sale_purchase_order_image.print_line_number", self.print_line_number)
        ICPSudo.set_param("sale_purchase_order_image.print_product_image", self.print_product_image)
        ICPSudo.set_param("sale_purchase_order_image.purchase_print_line_number", self.purchase_print_line_number)
        ICPSudo.set_param("sale_purchase_order_image.purchase_print_product_image", self.purchase_print_product_image)
#         if self.when_to_pay == 'invoice_payment':
#             if self.commission_based_on == 'product_category' or self.commission_based_on == 'product_template':
#                 raise UserError(_("Sales Commission: You can not have commision based on product or category if you have selected when to pay is payment."))
    

class sale_order(models.Model):

    _inherit = 'sale.order'
    
    @api.model
    def _get_soprint_line_number(self):
        #check if print_line_number is globally set then by default print_line_number is true
        #is_print_line_number_set = self.env['ir.values'].get_default('res.config.settings', 'print_line_number')
        is_print_line_number_set = self.env['ir.config_parameter'].sudo().get_param('sale_purchase_order_image.print_line_number') #odoo11
        if is_print_line_number_set:
            return True
        return False
    
    @api.model
    def _get_soprint_product_image(self):
        #check if print_product_image is globally set then by default print_product_image is true
#         is_print_product_image_set = self.env['ir.values'].get_default('res.config.settings', 'print_product_image')
        is_print_product_image_set = self.env['ir.config_parameter'].sudo().get_param('sale_purchase_order_image.print_product_image') #odoo11
        if is_print_product_image_set:
            return True
        return False
    
    print_line_number = fields.Boolean('Print Line Number', default=_get_soprint_line_number)
    print_product_image = fields.Boolean('Print Product Image', default=_get_soprint_product_image)
    
    # @api.multi
    @api.onchange('print_product_image', 'print_line_number')
    def on_change_print_product_image(self):
        for line in self.order_line:
            line.print_product_image = self.print_product_image
            line.print_line_number = self.print_line_number
            
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    print_line_number = fields.Boolean('Print Line Number')
    print_product_image = fields.Boolean('Print Product Image')
#     prouduct_small_image = fields.Binary(related='product_id.image_small', string='Image')
    prouduct_small_image = fields.Binary(string='Image')
    
    # @api.multi
    @api.onchange('product_id')
    # def product_id_change(self):
    def product_id_change_custom(self):
        # res = super(sale_order_line, self).product_id_change()
        # self.prouduct_small_image = self.product_id.image_medium
        self.prouduct_small_image = self.product_id.image_1920
        # return res
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(sale_order_line, self).create(vals_list)
        if res.order_id.print_line_number:
            res.print_line_number = True
        if res.order_id.print_product_image:
            res.print_product_image = True
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
