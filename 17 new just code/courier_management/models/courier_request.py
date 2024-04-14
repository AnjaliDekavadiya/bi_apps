# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Albin P J(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CourierRequest(models.Model):
    """This is for creating courier requests"""
    _name = 'courier.request'
    _description = "Courier Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    state = fields.Selection(
        selection=[('new', 'New'), ('collected', 'Collected'),
                   ('invoiced', 'Invoiced'), ('dispatched', 'Dispatched'),
                   ('in_transit', 'In Transit'),
                   ('arrived_at_destination', 'Arrived At Destination'),
                   ('out_for_delivery', 'Out For Delivery'),
                   ('delivered', 'Delivered'), ('cancelled', 'Cancelled')],
        string="State", default='new', help="State of the courier request")
    name = fields.Char(string='Name', readonly=True, copy=False,
                       default='New', help="Sequence number")
    sender_id = fields.Many2one('res.partner',
                                string="Sender Name",
                                help="Name of The Sender", required=True)
    sender_address = fields.Char(string="Sender Address",
                                 help="Address Of The Sender")
    sender_mobile_number = fields.Char(string="Sender Phone Number",
                                       help="Mobile Number Of The Sender",
                                       related='sender_id.phone',
                                       readonly=False,
                                       required=True)
    sender_email = fields.Char(string="Sender Email",
                               help="Email Of The Sender",
                               related='sender_id.email',
                               readonly=False, required=True)
    sender_street = fields.Char(string="Sender Street",
                                related='sender_id.street', readonly=False,
                                help="Street of the sender")
    sender_street2 = fields.Char(string="Sender Second Street",
                                 related='sender_id.street2', readonly=False,
                                 help="Second street of the sender")
    sender_city = fields.Char(string="Sender City", related='sender_id.city',
                              readonly=False,
                              help="City of the sender")
    sender_state_id = fields.Many2one('res.country.state',
                                      string="Sender State",
                                      related='sender_id.state_id',
                                      readonly=False,
                                      domain="[('country_id', '=?', "
                                             "sender_address_country_id)]",
                                      help="State of the sender")
    sender_zip = fields.Char(string="Sender Zip", related='sender_id.zip',
                             help="Zip of the sender")
    sender_address_country_id = fields.Many2one('res.country',
                                                string="Sender Country Address",
                                                related='sender_id.country_id',
                                                readonly=False,
                                                help="Country of the sender")
    receiver_id = fields.Many2one('res.partner',
                                  string="Receiver Name",
                                  help="Name of the receiver", required=True)
    receiver_address = fields.Char(string="Receiver address",
                                   help="Address of the receiver")
    receiver_street = fields.Char(string="Receiver Street",
                                  related='receiver_id.street', readonly=False,
                                  help="Street of the receiver")
    receiver_street2 = fields.Char(string="Receiver Second Street",
                                   related='receiver_id.street2',
                                   readonly=False,
                                   help="Second street of the receiver")
    receiver_city = fields.Char(string="Receiver City",
                                related='receiver_id.city', readonly=False,
                                help="City of the receiver")
    receiver_state_id = fields.Many2one('res.country.state',
                                        string="Receiver State",
                                        related='receiver_id.state_id',
                                        readonly=False,
                                        domain="[('country_id', '=?', "
                                               "receiver_address_country_id)]",
                                        help="State of the receiver")
    receiver_zip = fields.Char(string="Receiver Zip", related='receiver_id.zip',
                               readonly=False,
                               help="Zip of the receiver")
    receiver_address_country_id = fields.Many2one('res.country',
                                                  string="Receiver Country "
                                                         "Address",
                                                  related='receiver_id.'
                                                          'country_id',
                                                  readonly=False,
                                                  help="Country of the "
                                                       "receiver")
    receiver_mobile_number = fields.Char(string="Receiver Phone Number",
                                         help="Mobile Number Of The Receiver",
                                         related='receiver_id.phone',
                                         readonly=False,
                                         required=True)
    receiver_email = fields.Char(string="Receiver Email", help="Email Of The "
                                                               "Receiver",
                                 related='receiver_id.email',
                                 readonly=False, required=True)
    registration_date = fields.Date(string="Registration Date",
                                    help="Courier Registration Date",
                                    default=date.today(),
                                    readonly=True)
    delivery_date = fields.Date(string="Delivery Date",
                                help="Courier Delivery Date", required=True)
    total_kilometres = fields.Float(string="Total Kilometres",
                                    help="Total Kilometers To Courier Sends",
                                    required=True)
    distance_amount = fields.Monetary(string="Distance Amount",
                                      compute='_compute_distance_amount',
                                      store=True,
                                      help="Distance amount based on the "
                                           "distance")
    responsible_user_id = fields.Many2one('res.users',
                                          default=lambda self: self.env.user,
                                          string="Responsible User",
                                          help="Responsible User Of This "
                                               "Courier",
                                          readonly=True)
    type_id = fields.Many2one('courier.type', string="Type",
                              required=True, help="Courier type")
    tag_ids = fields.Many2many('courier.tag', string="Tag",
                               help="Courier tags")
    l_w_h_id = fields.Many2one('courier.dimension.price',
                               string="L X W X H", required=True,
                               help="Courier box size")
    volumetric_weight = fields.Float(string="Volumetric Weight",
                                     related='l_w_h_id.volumetric_weight',
                                     help="Weight of the courier")
    volumetric_weight_price = fields.Monetary(string="Volumetric Weight Price",
                                              compute='_compute_volumetric_'
                                                      'weight_price',
                                              help="Weight price of the courier"
                                              )
    priority_id = fields.Many2one('courier.priority',
                                  string="Priority", help="Courier priority")
    priority_amount = fields.Monetary(string="Priority Amount",
                                      compute='_compute_priority_amount',
                                      readonly=True,
                                      help="Courier priority amount based on "
                                           "priority")
    category_id = fields.Many2one('courier.category',
                                  string="Category", required=True,
                                  help="Courier category")
    description = fields.Char(string="Description", help="Add description")
    internal_note = fields.Char(string="Internal Note", help="Add internal "
                                                             "note")
    total_courier_charges = fields.Float(string="Total Courier Charges",
                                         readonly=True,
                                         help="The total courier charges")
    total = fields.Monetary(string="Total", compute='_compute_total',
                            readonly=True, help="Total")
    company_id = fields.Many2one('res.company', string="Company",
                                 required=True,
                                 default=lambda self: self.env.company,
                                 readonly=True, help="Choose company")
    currency_id = fields.Many2one("res.currency", string='Currency',
                                  related='company_id.currency_id',
                                  help="Company currency")
    courier_details_ids = fields.One2many('courier.detail',
                                          'courier_requests_id',
                                          string="Courier Details",
                                          help="Courier details")

    def action_collected(self):
        """This will change the state to collected or give validation error"""
        for record in self:
            if record.courier_details_ids:
                self.state = 'collected'
            else:
                raise ValidationError(_(
                    'You Need To Add A Line Before Collecting'))

    def action_dispatched(self):
        """This will change the state to dispatched"""
        self.state = 'dispatched'

    def action_in_transit(self):
        """This will change the state to in transit"""
        self.state = 'in_transit'

    def action_arrived_at_destination(self):
        """This will change the state to arrived at destination"""
        self.state = 'arrived_at_destination'

    def action_out_for_delivery(self):
        """This will change the state to out for delivery"""
        self.state = 'out_for_delivery'

    def action_delivered(self):
        """This will change the state to delivered"""
        self.state = 'delivered'

    def action_cancelled(self):
        """This will change the state to cancelled"""
        self.state = 'cancelled'

    @api.onchange('delivery_date')
    def _onchange_delivery_date(self):
        """If the delivery date is smaller than registration date. It gives
        a validation error"""
        if self.delivery_date and self.delivery_date <= self.registration_date:
            raise ValidationError(_('Delivery Is Not Possible On This Date'))

    @api.onchange('total_kilometres')
    def _onchange_total_kilometres(self):
        """If the total kilometres is smaller than one.It gives a validation"""
        if self.total_kilometres and self.total_kilometres < 1:
            raise ValidationError(_('Delivery Is Not Available'))

    def action_create_invoice(self):
        """Creating invoices for corresponding courier request"""
        self.state = 'invoiced'
        for rec in self:
            invoice_id = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': rec.sender_id.id,
                'invoice_date': rec.registration_date,
                'invoice_user_id': rec.responsible_user_id.id,
                'courier_ref_id': rec.id
            })
        for courier_order_line in self.courier_details_ids:
            invoice_id.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': courier_order_line.product_id.id,
                    'quantity': 1,
                    'price_unit': courier_order_line.weight_price,
                })]
            })
        if self.l_w_h_id:
            invoice_id.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.env.ref(
                        'courier_management.'
                        'volumetric_weight_charges_product').id,
                })]
            })
        if self.priority_id:
            invoice_id.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.env.ref(
                        'courier_management.'
                        'additional_charges_priority_product').id,
                })]
            })
        if self.total_kilometres:
            invoice_id.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': self.env.ref(
                        'courier_management.distance_charges_product').id,
                })]
            })

    def action_view_invoices(self):
        """It returns the Invoices tree view"""
        return {
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': [('courier_ref_id', '=', self.id)],
            'context': "{'create': False}"
        }

    @api.onchange('courier_details_ids')
    def _onchange_courier_details_ids(self):
        """Returns the total courier charges"""
        total = 0
        courier = self.courier_details_ids
        total_charge = courier.mapped('sub_total')
        for record in range(0, len(total_charge)):
            total = total + total_charge[record]
            self.total_courier_charges = total

    @api.depends('priority_amount', 'distance_amount',
                 'total_courier_charges', 'volumetric_weight_price')
    def _compute_total(self):
        """Computes the total"""
        self.total = self.priority_amount + self.distance_amount + \
                     self.total_courier_charges + self.volumetric_weight_price

    @api.depends('total_kilometres')
    def _compute_distance_amount(self):
        """Returns the distance amount"""
        prices = []
        self.distance_amount = False
        for record in self.env['courier.distance.price'].search(
                [('minimum_distance', '<=', self.total_kilometres),
                 ('maximum_distance', '>=', self.total_kilometres)]):
            prices.append(record.price)
        if prices:
            self.distance_amount = min(prices)
        else:
            distances = self.env['courier.distance.price'].search([])
            minimum_distances = [rec.minimum_distance for rec in distances]
            maximum_distances = [rec.maximum_distance for rec in distances]
            prices = [rec.price for rec in distances]

            if self.total_kilometres < min(minimum_distances):
                self.distance_amount = min(prices)
            elif self.total_kilometres > max(maximum_distances):
                self.distance_amount = max(prices)

        distance = self.env['product.product'].browse(
            [self.env.ref('courier_management.distance_charges_product').id])
        distance.list_price = self.distance_amount

    @api.depends('priority_id')
    def _compute_priority_amount(self):
        """Returns the priority amount based on priority"""
        self.priority_amount = self.priority_id.charges
        priority = self.env['product.product'].browse(
            [self.env.ref(
                'courier_management.additional_charges_priority_product').id])
        priority.list_price = self.priority_amount

    @api.depends('l_w_h_id')
    def _compute_volumetric_weight_price(self):
        """Returns the volumetric weight price"""
        self.volumetric_weight_price = self.l_w_h_id.price
        volume = self.env['product.product'].browse(
            [self.env.ref(
                'courier_management.volumetric_weight_charges_product').id])
        volume.list_price = self.volumetric_weight_price

    @api.model_create_multi
    def create(self, vals_list):
        """This is used to get the Courier sequence number"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'courier.request') or 'New'
        result = super(CourierRequest, self).create(vals_list)
        return result
