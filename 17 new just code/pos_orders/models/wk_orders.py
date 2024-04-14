# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_all_orders(self, kwargs):
        records_by_session = self.search([('session_id.name', '=', kwargs.get('session_name'))])
        config_rec = self.env['pos.config'].search([('id', '=', kwargs.get('config_id'))])
        all_orders = self.search([('id', 'not in', kwargs.get('current_order'))])
        
        if config_rec.order_loading_options == 'current_session':
            orders = records_by_session
        elif config_rec.order_loading_options == 'all_orders':
            orders = all_orders

        records, lines = [], []

        for order in orders:
            all_records = {
                "id"           : order.id,
                "name"         : order.name,
                "amount_total" : order.amount_total,
                "payment_ids"  : order.payment_ids.ids,
                "account_move" : order.account_move.id,
                "date_order"   : order.date_order + \
                    timedelta(hours=5, minutes=30),
                "lines"        : lines,
                "pos_reference": order.pos_reference,
                "partner_id"   : [order.partner_id.id, order.partner_id.name],

            }
            all_lines = {}
            all_payments = {}
            if hasattr(order[0], 'return_status'):
                if not order.is_return_order:
                    all_records['return_status'] = order.return_status
                    all_records['existing'] = False
                    all_records['id'] = order.id
                else:
                    order.return_order_id.return_status = order.return_status
                    all_records['existing'] = True
                    all_records['id'] = order.id
                    all_records['original_order_id'] = order.return_order_id.id
                    all_records['return_status'] = order.return_order_id.return_status
                i = 0
                if order in all_orders:
                    for line in order.lines:
                        all_lines[i] = {
                            'discount'             : line.discount,
                            'id'                   : line.id,
                            'order_id'             : [line.order_id.id, line.order_id.name],
                            'price_subtotal'       : line.price_subtotal,
                            'price_subtotal_incl'  : line.price_subtotal_incl,
                            'price_unit'           : line.price_unit,
                            'line_qty_returned'    : line.original_line_id.line_qty_returned,
                            'product_id'           : [line.product_id.id, line.product_id.name],
                            'qty'                  : line.qty,
                        }
                        i += 1
                        lines.append(line.id)
                    for payment_id in order.payment_ids:
                        all_payments[i] = {
                            'amount'      : payment_id.amount,
                            'id'          : payment_id.id,
                        }
                        if payment_id.payment_method_id:
                            all_payments[i]['journal_id'] = [payment_id.payment_method_id.id,
                                                            payment_id.payment_method_id.name]
                        else:
                            all_payments[i]['journal_id'] = False
                        records.append(all_payments[i])
            records.append(all_records)
            records.append(all_lines)
        return records

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order_id in order_ids:
            order_list = []
            order_line_list = []
            payment_list = []
            if(order_id.get('id')):
                order = self.browse([order_id.get('id')])
                vals = {
                    'lines'          : [],
                    'statment_ids'   : [obj.payment_method_id for obj in order.payment_ids],
                    'name'           : order.name,
                    'amount_total'   : order.amount_total,
                    'pos_reference'  : order.pos_reference,
                    'date_order'     : order.date_order,

                }
                # vals['lines'] = []
                if hasattr(order[0], 'return_status'):
                    if not order.is_return_order:
                        vals['return_status'] = order.return_status
                        vals['existing'] = False
                        vals['id'] = order.id
                    else:
                        order.return_order_id.return_status = order.return_status
                        vals['existing'] = True
                        vals['id'] = order.id
                        vals['original_order_id'] = order.return_order_id.id
                        vals['return_status'] = order.return_order_id.return_status
                        for line in order.lines:
                            line_vals = {}
                            if line.original_line_id:
                                line_vals['id'] = line.original_line_id.id
                                line_vals['line_qty_returned'] = line.original_line_id.line_qty_returned
                                line_vals['existing'] = True
                            order_line_list.append(line_vals)
                if order.account_move:
                    vals['invoice_id'] = order.account_move.id
                else:
                    vals['invoice_id'] = False
                if order.partner_id:
                    vals['partner_id'] = [
                        order.partner_id.id, order.partner_id.name]
                else:
                    vals['partner_id'] = False
                if (not hasattr(order[0], 'return_status') or (hasattr(order[0], 'return_status') and not order.is_return_order)):
                    vals['id'] = order.id
                    for line in order.lines:
                        vals['lines'].append(line.id)
                        # LINE DATA
                        line_vals = {
                            'create_date'        : line.create_date,
                            'discount'           : line.discount,
                            'display_name'       : line.display_name,
                            'id'                 : line.id,
                            'order_id'           : [line.order_id.id, line.order_id.name],
                            'price_subtotal'     : line.price_subtotal,
                            'price_subtotal_incl': line.price_subtotal_incl,
                            'price_unit'         : line.price_unit,
                            'product_id'         : [line.product_id.id, line.product_id.name],
                            'qty'                : line.qty, 
                            'write_date'         : line.write_date,
                        }
                        if hasattr(line, 'line_qty_returned'):
                            line_vals['line_qty_returned'] = line.line_qty_returned
                        # LINE DATA
                        order_line_list.append(line_vals)
                    for payment_id in order.payment_ids:
                        # STATEMENT DATA
                        payment_vals = {
                            'amount':payment_id.amount,
                            'id'    :payment_id.id,
                        }
                        if payment_id.payment_method_id:
                            currency = payment_id.payment_method_id.company_id.currency_id
                            payment_vals['journal_id'] = [payment_id.payment_method_id.id,
                                                          payment_id.payment_method_id.name + " (" + currency.name+")"]
                        else:
                            payment_vals['journal_id'] = False
                        payment_list.append(payment_vals)
                order_list.append(vals)
            order_id['orders'] = order_list
            order_id['orderlines'] = order_line_list
            order_id['payments'] = payment_list
        return order_ids

class PosConfig(models.Model):
    _inherit = 'pos.config'

    order_loading_options = fields.Selection([("current_session", "Load Orders Of Current Session"), (
        "all_orders", "Load All Past Orders"), ("n_days", "Load Orders Of Last 'n' Days")], default='current_session', string="Loading Options")
    number_of_days = fields.Integer(string='Number Of Past Days', default=10)

    @api.constrains('number_of_days')
    def number_of_days_validation(self):
        if self.order_loading_options == 'n_days':
            if not self.number_of_days or self.number_of_days < 0:
                raise ValidationError(
                    "Please provide a valid value for the field 'Number Of Past Days'!!!")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_order_loading_options = fields.Selection(related='pos_config_id.order_loading_options', readonly=False)
    pos_number_of_days = fields.Integer(related='pos_config_id.number_of_days', readonly=False)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model_pos_order = 'pos.order'
        if new_model_pos_order not in result:
            result.append(new_model_pos_order)
        new_model_pos_order_line = 'pos.order.line'
        if new_model_pos_order_line not in result:
            result.append(new_model_pos_order_line)
        return result

    def _loader_params_pos_order(self):
        domain_list = []
        if self.config_id.order_loading_options == 'n_days':
            today = datetime.today()
            validation_date = today + \
               timedelta(
                    days=(-1*int(self.config_id.number_of_days)))
            domain_list = [('date_order', '>', fields.Datetime.to_string(
                validation_date)), ('state', 'not in', ['draft', 'cancel'])]
        elif self.config_id.order_loading_options == 'current_session':
            domain_list = [('session_id', '=', self.name),
                           ('state', 'not in', ['draft', 'cancel'])]
        else:
            domain_list = [('state', 'not in', ['draft', 'cancel'])]

        model_fields = ['id', 'name', 'date_order',
                        'partner_id', 'lines', 'pos_reference', 'account_move']
        return {'search_params': {'domain': domain_list, 'fields': model_fields}}

    def _get_pos_ui_pos_order(self, params):
        pos_orders = self.env['pos.order'].search_read(
            **params['search_params'])
        return pos_orders

    def _loader_params_pos_order_line(self):
        pos_order_ids = self.env['pos.order'].search(self._loader_params_pos_order()[
                                                    'search_params']['domain']).ids
        fields = ['product_id', 'order_id', 'qty', 'discount',
                  'price_unit', 'price_subtotal_incl', 'price_subtotal']
        return {'search_params': {'domain': [('order_id', 'in', pos_order_ids)], 'fields': fields}}

    def _get_pos_ui_pos_order_line(self, params):
        pos_order_lines = self.env['pos.order.line'].search_read(**params['search_params'])
        return pos_order_lines
