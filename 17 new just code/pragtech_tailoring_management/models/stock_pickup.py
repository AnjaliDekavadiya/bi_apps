from odoo import fields, models, api, _
from odoo.exceptions import MissingError, ValidationError


class StockPickup(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one('res.users', string="Driver")
    image_filename = fields.Char(string="Image Filename")
    state = fields.Selection(selection_add=[('delivered', 'DELIVERED')])
    is_delivery = fields.Boolean(default=False, compute='is_delivery_funct')
    otp_verified = fields.Boolean(default=False)
    otp = fields.Char(string='OTP Number')
    delivered_date = fields.Datetime(string="Delivered Date")

    # ...........................................Stock Validate Button..........................................

    @api.depends('otp')
    def _compute_is_delivery(self):
        for record in self:
            if record.otp == record.sale_id.random_number:
                record.otp_verified = True
            else:
                raise ValidationError("The OTP is not correct, please try again later")

    def button_validate(self):
        pic = super(StockPickup, self).button_validate()

        if self.state == 'done':
            sale_order = self.sale_id
            if sale_order:
                sale_order.write({'state': 'shipped'})

        stock_picking = self.browse(self.id)
        template = self.env.ref('pragtech_tailoring_management.mail_template_ready_to_shipped')
        email_values = {
            'email_from': self.company_id.email,
            'email_to': self.partner_id.email,
            'subject': 'Shipped',
        }
        template.send_mail(stock_picking.id, force_send=True, email_values=email_values)

        return pic

    # ...........................................Product Deliverd Button..........................................
    def delivered(self):
        self._compute_is_delivery()
        if not self.otp_verified and self.is_delivery:
            raise ValidationError(_("Please add the correct OTP."))
        if self.state == 'done':
            sale_orders = self.env['sale.order'].search([('picking_ids', 'in', self.ids)])
            for sale_order in sale_orders:
                if sale_order.state != 'delivered':
                    sale_order.state = 'delivered'
            self.state = 'delivered'

        # Trigger the email function when the 'delivered' function is called
        self.send_delivered_product_email()

    @api.depends('is_delivery')
    def is_delivery_funct(self):
        if self.picking_type_id.code == 'outgoing':
            self.is_delivery = True
        elif self.picking_type_id.code == 'incoming':
            self.is_delivery = False

    # @api.depends('state', 'picking_type_id', 'photo_req')
    # def photo_req_funct(self):
    #     if self.state == 'done' and self.picking_type_id.code == 'outgoing':
    #         self.photo_req = True
    #     else :
    #         self.photo_req = False

    def send_delivered_product_email(self):
        stock_picking = self.env['stock.picking'].browse(self.id)
        product = []
        for rec in self.move_ids_without_package:
            product.append(rec.product_id.name)
        template = self.env.ref('pragtech_tailoring_management.mail_template_delivered_product')
        email_values = {
            'email_from': self.company_id.email,
            'email_to': self.partner_id.email,
            'subject': 'Product Delivery',
        }
        template.send_mail(stock_picking.id, force_send=True, email_values=email_values)
