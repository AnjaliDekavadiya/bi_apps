from odoo import models, fields, api
from odoo.exceptions import UserError


# Whatsapp section configuration
class PosConfig(models.Model):
    _inherit = "pos.config"

    otp_total_discount = fields.Float(compute="_default_otp_total_discount")
    # otp_order_line_discount = fields.Float(compute="_default_otp_order_line_discount")
    otp_whatsapp_template_id = fields.Float(compute="_default_otp_whatsapp_template_id")
    otp_contact_id = fields.Float(compute="_default_otp_contact_id")

    def _default_otp_contact_id(self):
        self.otp_contact_id = self.env['ir.config_parameter'].sudo().get_param(
            'dr_discount_otp_auth.contact_id')

    def _default_otp_whatsapp_template_id(self):
        self.otp_whatsapp_template_id = self.env['ir.config_parameter'].sudo().get_param(
            'dr_discount_otp_auth.whatsapp_template_id')

    def _default_otp_total_discount(self):
        self.otp_total_discount = self.env['ir.config_parameter'].sudo().get_param(
            'dr_discount_otp_auth.otp_total_discount')

    # def _default_otp_order_line_discount(self):
    #     self.otp_order_line_discount = self.env['ir.config_parameter'].sudo().get_param('discount_otp_auth.otp_order_line_discount')