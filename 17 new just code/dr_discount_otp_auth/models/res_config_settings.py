from odoo import models, fields, api
from odoo.exceptions import UserError


# Whatsapp section configuration
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contact_id = fields.Many2one("res.users", string="Contacts", config_parameter="dr_discount_otp_auth.contact_id", required=True)
    # meta template id => 266169879520417 that work fine with POS.
    whatsapp_template_id = fields.Many2one("whatsapp.template", string="Template", config_parameter="dr_discount_otp_auth.whatsapp_template_id", domain="[('name', '=', 'admin_discount_approval'), ('language','=', 'en_US')]", required=True )

    otp_total_discount = fields.Float(string="OTP Discount", config_parameter="dr_discount_otp_auth.otp_total_discount")
    # otp_order_line_discount = fields.Float(string="OTP Order Line Discount", config_parameter="discount_otp_auth.otp_order_line_discount")






