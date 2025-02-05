# -*- coding: utf-8 -*-
# Copyright 2023 IZI PT Solusi Usaha Mudah
from pytz import timezone
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import timeit
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'mp.base']
    _rec_mp_order_statuses = {}
    _rec_mp_order_status_notes = {}
    _sql_constraints = [
        ('unique_mp_invoice_number', 'UNIQUE(mp_invoice_number)',
         'This Invoice Number is exists, please try another Marketplace Invoice Number')
    ]

    MP_ORDER_STATUSES = [
        ('new', 'New'),
        ('waiting', 'Waiting Payment'),
        ('to_cancel', 'To Cancel'),
        ('cancel', 'Cancelled'),
        ('to_process', 'To Process'),
        ('in_process', 'In Process'),
        ('to_ship', 'To Ship'),
        ('in_ship', 'In Shipping'),
        ('delivered', 'Delivered'),
        ('done', 'Done'),
        ('return', 'Returned'),
    ]

    MP_DELIVERY_TYPES = [
        ('pickup', 'Pickup'),
        ('drop off', 'Drop Off'),
        ('both', 'Pickup & Drop Off'),
        ('send_to_warehouse', 'Send to Warehouse')
    ]

    # MP Account
    mp_account_id = fields.Many2one(required=False)

    # MP Order Status
    mp_order_status = fields.Selection(string="MP Order Status", selection=MP_ORDER_STATUSES, required=False,
                                       store=True, compute="_compute_mp_order_status")
    mp_order_status_notes = fields.Char(string="MP Order Status Notes",
                                        compute="_compute_mp_order_status", compute_sudo=True)

    # MP Order Transaction & Payment
    mp_invoice_number = fields.Char(string="MP Invoice Number", required=False, index=True)
    mp_payment_method_info = fields.Char(string="MP Payment Method", required=False, readonly=True)
    mp_payment_date = fields.Datetime(string="MP Order Payment Date", readonly=True)
    mp_order_date = fields.Datetime(string="MP Order Date", readonly=True)
    mp_order_last_update_date = fields.Datetime(string="MP Order Last Update Date", readonly=True)
    mp_accept_deadline = fields.Datetime(string="Maximum Confirmation Date", readonly=True)
    mp_cancel_reason = fields.Char(string='MP Order Cancel Reason', readonly=True)
    mp_order_notes = fields.Text(string='MP Order Notes', readonly=True)

    # MP Order Shipment
    mp_awb_number = fields.Char(string="AWB Number", required=False)
    mp_awb_url = fields.Text(string="AWB URL", required=False, readonly=True)
    mp_awb_html = fields.Text(string="AWB HTML", readonly=True)
    mp_delivery_carrier_name = fields.Char(string="Delivery Carrier Name", readonly=True)
    mp_delivery_carrier_type = fields.Char(string="Delivery Carrier Type", readonly=True)
    mp_delivery_type = fields.Selection(
        string="Delivery Type", selection=MP_DELIVERY_TYPES, required=False, readonly=True)
    mp_shipping_deadline = fields.Datetime(string="Maximum Shpping Date", readonly=True)
    mp_delivery_weight = fields.Float(string="Weight (KG)", readonly=True)
    mp_delivery_cost = fields.Float(string="Delivery Cost", readonly=True)
    mp_awb_datas = fields.Binary(string='AWB URL Datas', attachment=True)
    mp_package_id = fields.Char(string='Package ID', readonly=True)

    # MP Buyer Info
    mp_buyer_id = fields.Char(string="Buyer ID", readonly=True)
    mp_buyer_username = fields.Char(string="Buyer Username", readonly=True)
    mp_buyer_name = fields.Char(string="Buyer Name", readonly=True)
    mp_buyer_email = fields.Char(string="Buyer Email", readonly=True)
    mp_buyer_phone = fields.Char(string="Buyer Phone", readonly=True)

    # MP Recipient Info
    mp_recipient_address_name = fields.Char(string="Recipient Name", readonly=True)
    mp_recipient_address_phone = fields.Char(string="Recipient Phone", readonly=True)
    mp_recipient_address_full = fields.Text(string="Recipient Full Address", readonly=True)
    mp_recipient_address_district = fields.Char(string="Recipient District", readonly=True)
    mp_recipient_address_city = fields.Char(string="Recipient City", readonly=True)
    mp_recipient_address_state = fields.Char(string="Recipient State", readonly=True)
    mp_recipient_address_country = fields.Char(string="Recipient Country", readonly=True)
    mp_recipient_address_zip = fields.Char(string="Recipient ZIP", readonly=True)

    # MP Amounts
    mp_amount_total = fields.Monetary(string="MP Total", readonly=True)
    mp_amount_total_info = fields.Char(string="MP Total Info", compute="_compute_mp_amount_total_info")
    mp_expected_income = fields.Monetary(string="Seller Expected Income", readonly=True)
    # Pre Order
    is_preorder = fields.Boolean(string='Is PreOrder ?')

    @classmethod
    def _build_model_attributes(cls, pool):
        super(SaleOrder, cls)._build_model_attributes(pool)
        cls._add_rec_mp_order_status()

    @classmethod
    def _add_rec_mp_order_status(cls, mp_order_statuses=None, mp_order_status_notes=None):
        if mp_order_statuses:
            cls._rec_mp_order_statuses = dict(cls._rec_mp_order_statuses, **dict(mp_order_statuses))
        if mp_order_status_notes:
            cls._rec_mp_order_status_notes = dict(cls._rec_mp_order_status_notes, **dict(mp_order_status_notes))

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for so in self:
            if so.mp_account_id and so.mp_account_id.create_invoice:
                for line in so.order_line:
                    if line.product_type == 'product':
                        if line.product_id.invoice_policy == 'delivery':
                            line.product_id.invoice_policy = 'order'
                if so.invoice_status == 'to invoice':
                    so._create_invoices(final=True)
                for move in so.invoice_ids:
                    if move.state == 'draft':
                        move.action_post()
            if so.mp_account_id and so.mp_account_id.keep_order_date:
                so.write({'date_order': so.mp_order_date})
        return res

    @api.model
    def create(self, vals):
        timer = timeit.default_timer()  # CHECK_DURATION
        res = super(SaleOrder, self).create(vals)
        _logger.info('CHECK_DURATION > Create Sales Order %s' % ((timeit.default_timer() - timer)))
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        timer = timeit.default_timer()  # CHECK_DURATION
        res = super(SaleOrder, self)._create_invoices(grouped, final, date)
        _logger.info('CHECK_DURATION > Create Invoice From Sales Order %s' % ((timeit.default_timer() - timer)))
        return res

    def write(self, values):
        res = super(SaleOrder, self).write(values)
        for so in self:
            if so.mp_awb_number and so.picking_ids:
                for picking in so.picking_ids:
                    picking.carrier_tracking_ref = so.mp_awb_number

        return res

    def action_cancel(self):
        for so in self:
            if so.mp_account_id and so.mp_account_id.create_invoice:
                for move in so.invoice_ids:
                    if move.state == 'posted':
                        move.button_draft()
                        move.button_cancel()
                    elif move.state == 'draft':
                        move.button_cancel()
        try:
            res = super(SaleOrder, self).action_cancel()
        except Exception as e:
            if str(e.args[0]) == "You cannot cancel a stock move that has been set to 'Done'." and self.sp_order_status == 'CANCELLED':
                res = super(SaleOrder, self).write({
                    'state': 'cancel'
                })
            else:
                res = super(SaleOrder, self).action_cancel()
        return res

    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        tz = timezone(self.env.context.get('tz') or 'Asia/Jakarta')
        for order in self:
            if order.mp_account_id:
                res['mp_invoice_number'] = order.mp_invoice_number
                res['mp_account_id'] = order.mp_account_id.id
                res['invoice_date'] = order.mp_order_date.astimezone(tz).date()
        return res

    @api.model
    def _finish_mapping_raw_data(self, sanitized_data, values):
        sanitized_data, values = super(SaleOrder, self)._finish_mapping_raw_data(sanitized_data, values)
        mp_account = self.get_mp_account_from_context()
        if not self._context.get('check', False):
            partner_shipping, customer = self.get_mp_order_customer(mp_account, values)
            partner_invoice = partner_shipping
            if mp_account.partner_id and mp_account.partner_id_as_partner_invoice is True:
                partner_invoice = mp_account.partner_id
            values.update({
                'partner_id': customer.id,
                'partner_invoice_id': partner_invoice.id,
                'partner_shipping_id': partner_shipping.id,
            })
        values.update({
            'company_id': mp_account.company_id.id
        })
        if mp_account.warehouse_id:
            values.update({
                'warehouse_id': mp_account.warehouse_id.id,
            })
        if mp_account.team_id:
            values.update({
                'team_id': mp_account.team_id.id,
            })
        else:
            values.update({
                'team_id': False,
            })
        if mp_account.user_id:
            values.update({
                'user_id': mp_account.user_id.id,
            })
        if mp_account.payment_term_id:
            values.update({
                'payment_term_id': mp_account.payment_term_id.id,
            })
        if mp_account.pricelist_id:
            values.update({
                'pricelist_id': mp_account.pricelist_id.id,
            })
        return sanitized_data, values

    @api.model
    def _finish_create_records(self, records):
        records = super(SaleOrder, self)._finish_create_records(records)
        records = self.process_order_component_config(records)
        record_ids_to_confirm = []
        # record_ids_to_cancel = []
        allowed_order_status = ['to_process', 'in_process', 'to_ship', 'in_ship', 'delivered', 'done']
        if records.exists():
            records = records.exists()
            for rec in records:
                if rec.mp_account_id.auto_confirm is True:
                    if rec.mp_order_status in allowed_order_status:
                        if rec.state == 'draft':
                            record_ids_to_confirm.append(rec.id)
                if rec.mp_order_status == 'cancel':
                    if rec.state != 'cancel' and rec.state != 'done':
                        rec.with_context({'disable_cancel_warning': True}).action_cancel()
                        # record_ids_to_cancel.append(rec.id)
            for record in records.filtered(lambda r: r.id in record_ids_to_confirm):
                record.action_confirm()
                if hasattr(record, '%s_ship_order' % record.marketplace):
                    getattr(record, '%s_ship_order' % record.marketplace)()
            # records.filtered(lambda r: r.id in record_ids_to_cancel).action_cancel()
        records = records.exists()
        return records

    @api.model
    def _finish_update_records(self, records):
        records = super(SaleOrder, self)._finish_update_records(records)
        records = self.process_order_component_config(records)
        record_ids_to_confirm = []
        # record_ids_to_cancel = []
        allowed_order_status = ['to_process', 'in_process', 'to_ship', 'in_ship', 'delivered', 'done']
        for rec in records:
            if rec.mp_account_id.auto_confirm is True:
                if rec.mp_order_status in allowed_order_status:
                    if rec.state == 'draft':
                        record_ids_to_confirm.append(rec.id)
            if rec.mp_order_status == 'cancel':
                if rec.state != 'cancel' and rec.state != 'done':
                    rec.with_context({'disable_cancel_warning': True}).action_cancel()
                    # record_ids_to_cancel.append(rec.id)
        for record in records.filtered(lambda r: r.id in record_ids_to_confirm):
            record.action_confirm()
        # records.filtered(lambda r: r.id in record_ids_to_cancel).action_cancel()
        return records

    # @api.multi
    def _compute_mp_order_status(self):
        for order in self:
            _new_rec_mp_order_statuses = order._rec_mp_order_statuses
            _new_rec_mp_order_status_notes = order._rec_mp_order_status_notes
            if hasattr(self, '%s_add_rec_mp_order_status' % order.marketplace):
                mp_order_statuses,mp_order_status_notes = getattr(self, '%s_add_rec_mp_order_status' % order.marketplace)()
                _new_rec_mp_order_statuses = dict(order._rec_mp_order_statuses, **dict(mp_order_statuses))
                _new_rec_mp_order_status_notes = dict(order._rec_mp_order_status_notes, **dict(mp_order_status_notes))
            
            if order.marketplace not in _new_rec_mp_order_statuses.keys():
                order.mp_order_status = None
            else:
                mp_order_status_field, mp_order_statuses = _new_rec_mp_order_statuses[order.marketplace]
                mp_order_status_value = 'new'
                for mp_order_status, mp_order_status_codes in mp_order_statuses.items():
                    if getattr(order, mp_order_status_field) in mp_order_status_codes:
                        mp_order_status_value = mp_order_status
                        break
                order.mp_order_status = mp_order_status_value

            if order.marketplace not in _new_rec_mp_order_status_notes.keys():
                order.mp_order_status_notes = None
            else:
                mp_order_status_notes = _new_rec_mp_order_status_notes[order.marketplace]
                if order.mp_order_status:
                    default_notes = 'Status code "%s" is not registered in our apps, it may be new status code added ' \
                                    'by %s. Please report this to our developer team! ' % (
                                        order.mp_order_status, order.marketplace.upper())
                    order.mp_order_status_notes = mp_order_status_notes.get(order.mp_order_status, default_notes)
                else:
                    order.mp_order_status_notes = None

    # @api.multi
    def _compute_mp_amount_total_info(self):
        for order in self:
            order.mp_amount_total_info = False
            if order.amount_total != order.mp_amount_total:
                order.mp_amount_total_info = "WARNING: Amount total of Sale Order is different with amount total of " \
                                             "marketplace order! "

    @api.model
    def lookup_partner_shipping(self, order_values, default_customer=None):
        partner_obj = self.env['res.partner']
        mp_account_id = order_values.get('mp_account_id')
        if not default_customer:
            default_customer = partner_obj
        partner_shipping = partner_obj
        partner_shipping_values = {
            'name': order_values.get('mp_recipient_address_name'),
            'phone': order_values.get('mp_recipient_address_phone'),
            'street': order_values.get('mp_recipient_address_full'),
            'zip': order_values.get('mp_recipient_address_zip')
        }

        if default_customer.exists():  # Then look for child partner (delivery address) of default customer
            if order_values.get('mp_recipient_address_phone'):
                if mp_account_id not in default_customer.mp_account_ids.ids:
                    default_customer.write({
                        'mp_account_ids': [(4, mp_account_id)]
                    })
                partner_shipping = partner_obj.search([
                    ('parent_id', '=', default_customer.id),
                    ('phone', '=', order_values.get('mp_recipient_address_phone'))
                ], limit=1)
            if not partner_shipping.exists():  # Then create new child partner of default customer
                partner_shipping_values.update({'parent_id': default_customer.id, 'type': 'delivery'})
                partner_shipping = partner_obj.create(partner_shipping_values)
        else:  # Then look for child partner (delivery address) first
            if order_values.get('mp_recipient_address_phone'):
                partner_shipping = partner_obj.search([
                    ('parent_id', '!=', False),
                    ('type', '=', 'delivery'),
                    ('phone', '=', order_values.get('mp_recipient_address_phone'))
                ], limit=1)
                if not partner_shipping.exists():  # Then look for parent partner
                    partner = partner_obj.search([
                        ('parent_id', '=', False),
                        ('type', '=', 'contact'),
                        ('phone', '=', order_values.get('mp_recipient_address_phone'))
                    ], limit=1)
                    if not partner.exists():  # Then create partner
                        partner_values = partner_shipping_values.copy()
                        partner_values.update({
                            'type': 'contact',
                            'mp_account_ids': [(4, mp_account_id)]
                        })
                        partner = partner_obj.create(partner_values)
                    # Then pass it to this method recursively
                    return self.lookup_partner_shipping(order_values, default_customer=partner)
        # Finally return the partner shipping
        return partner_shipping

    @api.model
    def get_mp_order_customer(self, mp_account, values):
        partner_shipping = self.get_partner(mp_account, values)
        if not partner_shipping:
            partner_shipping = self.lookup_partner_shipping(values)
        # Finally return the partner shipping and its parent as customer
        return partner_shipping, partner_shipping.parent_id

    # @api.multi
    def generate_delivery_line(self):
        for order in self:
            if hasattr(order, '%s_generate_delivery_line' % order.marketplace):
                getattr(order, '%s_generate_delivery_line' % order.marketplace)()

    # @api.multi
    def generate_insurance_line(self):
        for order in self:
            if hasattr(order, '%s_generate_insurance_line' % order.marketplace):
                getattr(order, '%s_generate_insurance_line' % order.marketplace)()

    # @api.multi
    def generate_global_discount_line(self):
        for order in self:
            if hasattr(order, '%s_generate_global_discount_line' % order.marketplace):
                getattr(order, '%s_generate_global_discount_line' % order.marketplace)()

    # @api.multi
    def generate_adjusment_line(self):
        for order in self:
            if hasattr(order, '%s_generate_adjusment_line' % order.marketplace):
                getattr(order, '%s_generate_adjusment_line' % order.marketplace)()

    # @api.multi
    def process_order_component_config(self, records):
        if records.exists():
            records = records.exists()
            order_component_configs = self.env['order.component.config'].sudo().search(
                [('active', '=', True), ('mp_account_ids', 'in', self._context.get('mp_account_id'))])
            generate_delivery = True
            generate_discount = True
            generate_insurance = True
            generate_adjusment = True
            for component_config in order_component_configs:
                # Process to Remove Product First
                for line in component_config.line_ids:
                    if line.component_type == 'remove_product':
                        if line.remove_delivery:
                            generate_delivery = False
                        if line.remove_discount:
                            generate_discount = False
                        if line.remove_insurance:
                            generate_insurance = False
                        if line.remove_adjustment:
                            generate_adjusment = False
                        if line.remove_product_ids.ids:
                            for record in records:
                                for order_line in record.order_line:
                                    if order_line.product_id.id in line.remove_product_ids.ids:
                                        order_line.unlink()

                # Then Discount
                for line in component_config.line_ids:
                    if line.component_type == 'discount_line':
                        for record in records:
                            for order_line in record.order_line:
                                if order_line.is_global_discount or order_line.is_delivery or order_line.is_insurance or order_line.is_adjustment:
                                    continue
                                if line.discount_line_method == 'input':
                                    if line.discount_line_product_type == 'all' or (order_line.get('product_id', False) and order_line.get('product_id') in line.discount_line_product_ids.ids):
                                        price_unit = order_line.price_unit
                                        if 100 - line.percentage_value > 0:
                                            new_price_unit = round(100 * price_unit / (100 - line.percentage_value), 10)
                                        order_line.write({
                                            'price_unit': new_price_unit,
                                            'discount': line.percentage_value,
                                        })
                                elif line.discount_line_method == 'calculated':
                                    if line.discount_line_product_type == 'all' or (order_line.get('product_id', False) and order_line.get('product_id') in line.discount_line_product_ids.ids):
                                        price_unit = order_line.price_unit
                                        product = order_line.product_id
                                        qty = order_line.product_uom_qty
                                        if product:
                                            normal_price = 0
                                            if order_line.normal_price:
                                                normal_price = order_line.normal_price
                                            if normal_price == 0:
                                                for mp_product in product.map_line_ids:
                                                    if mp_product.mp_account_id == order_line.mp_account_id:
                                                        if mp_product.name == order_line.mp_product_name or mp_product.default_code == order_line.mp_product_sku:
                                                            if mp_product.mp_product_variant_id:
                                                                variant_obj = mp_product.mp_product_variant_id
                                                                for wholesale in variant_obj.mp_product_id.mp_product_wholesale_ids:
                                                                    if qty >= wholesale.min_qty and qty <= wholesale.max_qty:
                                                                        normal_price = wholesale.price
                                                                        break
                                                                if normal_price == 0:
                                                                    normal_price = variant_obj.list_price
                                                                    break
                                                            elif mp_product.mp_product_id:
                                                                mp_product_obj = mp_product.mp_product_id
                                                                for wholesale in mp_product_obj.mp_product_wholesale_ids:
                                                                    if qty >= wholesale.min_qty and qty <= wholesale.max_qty:
                                                                        normal_price = wholesale.price
                                                                        break
                                                                if normal_price == 0:
                                                                    normal_price = mp_product_obj.list_price
                                                                    break
                                            if normal_price == 0:
                                                normal_price = product.product_tmpl_id.list_price
                                                for tax in product.product_tmpl_id.taxes_id:
                                                    if tax.price_include:
                                                        continue
                                                    elif tax.amount_type == 'percent' and tax.amount > 0:
                                                        normal_price = normal_price = round(
                                                            normal_price * (100 + tax.amount) / 100, 10)
                                            # Direct
                                            if normal_price > 0:
                                                order_line.write({
                                                    'price_retail': normal_price,
                                                    'price_discount': normal_price - price_unit,
                                                    'price_unit': price_unit,
                                                })
                                            # Calculate Discount %
                                            # discount_percentage = 0
                                            # if normal_price > 0:
                                            #     discount_percentage = round(
                                            #         (normal_price - price_unit) * 100 / normal_price, 10)
                                            #     if discount_percentage > 0:
                                            #         order_line.write({
                                            #             'price_unit': normal_price,
                                            #             'discount': discount_percentage,
                                            #         })

                # Then Add Tax
                for line in component_config.line_ids:
                    if line.component_type == 'tax_line':
                        for record in records:
                            for order_line in record.order_line:
                                if order_line.is_global_discount or order_line.is_delivery or order_line.is_insurance or order_line.is_adjustment:
                                    continue
                                if line.account_tax_id and line.account_tax_id.amount_type == 'percent':
                                    percentage = line.account_tax_id.amount
                                    if percentage > 0:
                                        price_unit = order_line.get('price_unit')
                                        new_price = (price_unit * 100) / (100 + percentage)
                                        record.write({
                                            'order_line': [(0, 0, {
                                                'price_unit': new_price,
                                                'tax_id': [(6, 0, [line.account_tax_id.id])],
                                            })]
                                        })
                # Then Add Product
                for line in component_config.line_ids:
                    if line.component_type == 'add_product':
                        # Calculate Total Price
                        amount_total = 0
                        for record in records:
                            for order_line in record.order_line:
                                amount_total += order_line.get('price_total')

                        if line.additional_product_id:
                            price_unit = 0
                            if line.fixed_value:
                                price_unit = line.fixed_value
                            elif line.percentage_value:
                                price_unit = round(line.percentage_value * amount_total / 100)
                            record.write({
                                'order_line': [(0, 0, {
                                    'name': line.name,
                                    'product_id': line.additional_product_id.id,
                                    'product_uom_qty': 1.0,
                                    'price_subtotal': price_unit,
                                    'price_total': price_unit,
                                    'price_unit': price_unit,
                                    'discount': 0.0,
                                    'is_discount': True,
                                })]
                            })

            if generate_delivery:
                records.generate_delivery_line()
            if generate_discount:
                records.generate_global_discount_line()
            if generate_insurance:
                records.generate_insurance_line()
            if generate_adjusment:
                records.generate_adjusment_line()
        return records

    def confirm_order(self):
        for order in self:
            order.action_confirm()

    # @api.multi
    def accept_order(self):
        for order in self:
            if hasattr(order, '%s_accept_order' % order.marketplace):
                getattr(order, '%s_accept_order' % order.marketplace)()

    def fetch_order(self):
        for order in self:
            if hasattr(order, '%s_fetch_order' % order.marketplace):
                getattr(order, '%s_fetch_order' % order.marketplace)()

    # @api.multi
    def reject_order(self):
        marketplace = self.mapped('marketplace')
        mp_account_ids = self.mapped('mp_account_id.id')
        if marketplace.count(marketplace[0]) == len(marketplace):
            if mp_account_ids.count(mp_account_ids[0]) == len(mp_account_ids):
                if hasattr(self, '%s_reject_order' % marketplace[0]):
                    return getattr(self, '%s_reject_order' % marketplace[0])()
            else:
                raise ValidationError('Please select the same marketplace account.')
        else:
            raise ValidationError('Please select the same marketplace channel.')

    # @api.multi
    def get_label(self):
        marketplace = self.mapped('marketplace')
        mp_account_ids = self.mapped('mp_account_id.id')
        if marketplace.count(marketplace[0]) == len(marketplace):
            if mp_account_ids.count(mp_account_ids[0]) == len(mp_account_ids):
                if hasattr(self, '%s_print_label' % marketplace[0]):
                    return getattr(self, '%s_print_label' % marketplace[0])()
            else:
                raise ValidationError('Please select the same marketplace account.')
        else:
            raise ValidationError('Please select the same marketplace channel.')

    # @api.multi
    def get_awb_num(self):
        marketplace = self.mapped('marketplace')
        mp_account_ids = self.mapped('mp_account_id.id')
        if marketplace.count(marketplace[0]) == len(marketplace):
            if mp_account_ids.count(mp_account_ids[0]) == len(mp_account_ids):
                if hasattr(self, '%s_get_booking_code' % marketplace[0]):
                    return getattr(self, '%s_get_booking_code' % marketplace[0])()
                elif hasattr(self, '%s_get_awb_num' % marketplace[0]):
                    return getattr(self, '%s_get_awb_num' % marketplace[0])()
            else:
                raise ValidationError('Please select the same marketplace account.')
        else:
            raise ValidationError('Please select the same marketplace channel.')

    # @api.multi
    def request_pickup(self):
        marketplace = self.mapped('marketplace')
        mp_account_ids = self.mapped('mp_account_id.id')
        if marketplace.count(marketplace[0]) == len(marketplace):
            if mp_account_ids.count(mp_account_ids[0]) == len(mp_account_ids):
                if hasattr(self, '%s_request_pickup' % marketplace[0]):
                    return getattr(self, '%s_request_pickup' % marketplace[0])()
            else:
                raise ValidationError('Please select the same marketplace account.')
        else:
            raise ValidationError('Please select the same marketplace channel.')

    # @api.multi
    def drop_off(self):
        marketplace = self.mapped('marketplace')
        mp_account_ids = self.mapped('mp_account_id.id')
        if marketplace.count(marketplace[0]) == len(marketplace):
            if mp_account_ids.count(mp_account_ids[0]) == len(mp_account_ids):
                if hasattr(self, '%s_drop_off' % marketplace[0]):
                    return getattr(self, '%s_drop_off' % marketplace[0])()
                else:
                    return ValidationError('The feature is not available now for %s' % marketplace[0])
            else:
                raise ValidationError('Please select the same marketplace account.')
        else:
            raise ValidationError('Please select the same marketplace channel.')

    @api.model
    def get_partner(self, mp_account, order_values):
        if hasattr(self, '%s_get_partner' % mp_account.marketplace):
            default_customer = None
            if mp_account.partner_id:
                default_customer = mp_account.partner_id
            return getattr(self, '%s_get_partner' % mp_account.marketplace)(order_values, default_customer)

    def _can_be_confirmed(self):
        self.ensure_one()
        allowed_state = super(SaleOrder, self)._can_be_confirmed()
        if self.mp_account_id:
            if self.mp_account_id.auto_confirm:
                allowed_state = self.state in {'draft', 'sent', 'sale'}
        return allowed_state