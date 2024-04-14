# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
from odoo.http import request
import datetime
import pytz

class PosKitchenOrder(models.Model):
    _name = 'pos.kitchen.order'
    _order = 'id desc'
    _rec_name = 'pos_reference'
    _description = 'POS Kitchen Order'

    name = fields.Char(string="Name",readonly=True)
    is_changed = fields.Boolean(default=False, string="Is Changed",readonly=True)
    order_progress = fields.Selection([('new', 'New'), ('pending', 'Pending'),('partially_done', 'Partially Done'), ('done', 'Done'),('cancel', "Cancel") ], string="Order Progress",readonly=True)
    config_id = fields.Many2one('pos.config', string="POS Config",readonly=True)
    session_id = fields.Many2one('pos.session', string="POS Session",readonly=True)
    is_state_updated = fields.Boolean(string="Is state Updated",readonly=True)
    kitchen_order_name = fields.Char(string="Token NO.",readonly=True)
    user_id = fields.Many2one('res.users', string="Users",readonly=True)
    amount_total = fields.Float(string="Amount Total",readonly=True)
    out_of_stock_products = fields.One2many(
        'product.product', 'related_kitchen_order', string="Out Of Stock Products",readonly=True)
    cancellation_reason = fields.Char(string="Cancellation Reason",readonly=True)
    pos_reference = fields.Char(string="Pos Reference",readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner",readonly=True)
    date_order = fields.Datetime(string="DateTime",readonly=True)
    lines = fields.One2many('pos.kitchen.orderline',
                            'order_id', string="kitchen Orderlines" ,readonly=True)
    screen_progress = fields.Text(string="Screen Progress",readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(PosKitchenOrder, self).create(vals_list)
        print('------------------------------------kitchen order created')
        self.env['pos.session']._notify_changes_in_kitchen(records, False, records._name)
        return records
    
    def write(self, vals):
        res = super(PosKitchenOrder, self).write(vals)
        self.env['pos.session']._notify_changes_in_kitchen(self,False, self._name)
        return res

    def fetch_kitchen_order_data(self,config_id):
        """
            fetches orders to send it to show them on kitchen screen
            config_id: int,id of kitchen screen
            returns dict  with data of orders
        """
        pos_screen_data = self.env['pos.kitchen.screen.config'].sudo().browse(config_id)
        kitchen_orders = self.env['pos.kitchen.order'].sudo().search([])

        kitchen_orders = self.env['pos.kitchen.order'].sudo().search([('order_progress', 'in', ['new','pending', 'partially_done']), ('date_order', '>=', datetime.date.today()), ('config_id', 'in', pos_screen_data.pos_config_ids.ids)], order="id asc")
        print('------------------length----------fetch_kitchen_order_data', len(kitchen_orders))
        order_data = self.get_data_from_orders(True, pos_screen_data, pos_orders=[], restaurant_orders= kitchen_orders)
        order_data.update({'queue_order':pos_screen_data.queue_order})
        return order_data

    def get_data_from_orders(self, isUpdateTime, pos_screen_data, **kwargs):
        """
            gets updated order data 
            params:
            pos_screen_data:object of pos.kitchen.screen.config model 
            isUpdateTime:boolean
            kwargs:dict , keys as restaurant_orders and pos_orders
        """
        order_data = {
            'last_order_time': False,
            'order_data': [],
            'change_order_data': []
        }
        if (kwargs.get('pos_orders') and len(kwargs.get('pos_orders'))) or (kwargs.get('restaurant_orders') and len(kwargs.get('restaurant_orders')) or pos_screen_data.is_changed):
            orders_list = []
            if kwargs.get('pos_orders'):
                for order in kwargs.get('pos_orders'):
                    self.extract_order_data('pos',
                        order, orders_list, pos_screen_data)
                    if len(orders_list):
                        orders_list[-1]['order_type'] = 'pos'
            if kwargs.get('restaurant_orders'):
                for order in kwargs.get('restaurant_orders'):
                    self.extract_order_data('restaurant',
                        order, orders_list, pos_screen_data)
                    if len(orders_list):
                        orders_list[-1]['order_type'] = 'restaurant'
                        orders_list[-1]['floor_id'] = order.floor_id.name
                        orders_list[-1]['table_id'] = order.table_id.name
            sorted_list = sorted(
                orders_list, key=lambda l: l.get('order_date'))
            pos_screen_data = self.env['pos.kitchen.screen.config'].sudo().browse(
                kwargs.get('id'))
            if pos_screen_data.queue_order == "new2old":
                orders_list.reverse()
            order_data.update({
                'order_data': orders_list
            })
            if pos_screen_data.is_changed:
                changed_restaurant_orders = self.env['pos.kitchen.order'].sudo().search([('order_progress', 'in', ['cancel', 'pending', 'partially_done']), (
                    'date_order', '>=', datetime.date.today()), ('config_id', 'in', pos_screen_data.pos_config_ids.ids), ('is_changed', '=', True)], order="id asc")
                for order in changed_restaurant_orders:
                    vals = {'id': order.id, 'state': order.order_progress}
                    product_category_wise = {}
                    if order.order_progress in ['pending', 'partially_done']:
                        for line in order.lines:
                            if not line.is_orderline_done and not line.is_orderline_cancel:
                                count = 0
                                for categ in line.product_id.pos_categ_ids:
                                    if categ in pos_screen_data.pos_category_ids and not count:
                                        count += 1
                                        line_vals = {
                                            'note':hasattr(
                                            line, 'note') and line.note or '',
                                            'display_name':line.display_name,
                                            'id':line.id,
                                            'qty_added':line.qty_added,
                                            'state':line.state,
                                            'qty_removed':line.qty_removed,
                                            'order_id':[line.order_id.id, line.order_id.name],
                                            'done_line':"/pos/" + \
                                            str(line.id)+"/done/orderline",
                                            'screen_config':pos_screen_data.id,
                                            'product_id':[
                                            line.product_id.id, line.full_product_name or line.product_id.name],
                                            'qty':line.qty,
                                            'discount':line.discount,
                                        }
                                        categ_id = categ.name+'-'+str(categ.id)
                                        if categ_id not in product_category_wise:
                                            product_category_wise[categ_id] = {
                                                line.id: line_vals}
                                        else:
                                            product_category_wise[categ_id].update(
                                                {line.id: line_vals})                
                        vals['product_category_wise'] = product_category_wise
                    order_data['change_order_data'].append(vals)
                    order.sudo().write({'is_changed': False})
                pos_screen_data.sudo().write({'is_changed': False})
        return order_data

    def extract_order_data(self, order_type,order, orders_list, pos_screen_data):
        """
            takes order data and appends in orders_list 
            params:
            order_type:string,order type
            order:object of pos.kitchen.order model
            orders_list : list of dict of order data
        """
        session = self.env['pos.session'].sudo().browse(order.session_id.id)
        config_id = order.config_id
        pos_screen_data = pos_screen_data
        is_allowed_order = True
        has_category_product = []
        if len(pos_screen_data.pos_category_ids.ids):
            for line in order.lines:
                if not line.is_orderline_done and not line.is_orderline_cancel:
                    for cat in line.product_id.pos_categ_ids:
                        if cat.id in pos_screen_data.pos_category_ids.ids:
                            has_category_product.append(line.product_id)
            if len(has_category_product) == 0:
                is_allowed_order = False
        if is_allowed_order:
            order_date = order.date_order
            if request.env.context.get('tz'):
                user_tz = pytz.timezone(request.env.context.get('tz'))
                order_date = pytz.utc.localize(
                    order.date_order).astimezone(user_tz)
            order_progress = 'pending' if session.config_id.auto_accept else 'new'
            if order.order_progress:
                order_progress = order.order_progress
            vals = {
                'id':order.id,
                'lines':[],
                'name':order.name,
                'amount_total':order.amount_total,
                'pos_name':order.config_id.name,
                'pos_reference':order.pos_reference,
                'cancel_order':"/pos/"+str(order.id)+"/cancel/order",
                'confirm_order':"/pos/"+str(order.id)+"/confirm/order",
                'done_order':"/pos/"+str(order.id)+"/done/order",
                'cook_order':"/pos/"+str(order.id)+"/cook/order",
                'kitchen_order_name':order.kitchen_order_name,
                'order_date':order_date.strftime("%H:%M:%S"),
                'order_progress':order_progress,
                'orders_on_grid':int(pos_screen_data.orders_on_grid)
            }
            if int(pos_screen_data.orders_on_grid) % 3 == 0:
                vals['grid_class'] = "col-md-4 order-new"
            elif int(pos_screen_data.orders_on_grid) % 2 == 0:
                vals['grid_class'] = "col-md-6 order-new"
            else:
                vals['grid_class'] = "col-md-4 order-new"
            if order.partner_id:
                vals['partner_id'] = [
                    order.partner_id.id, order.partner_id.name]
            else:
                vals['partner_id'] = False
            product_category_wise = {}
            for line in order.lines:
                if not line.is_orderline_done and not line.is_orderline_cancel:
                    count = 0
                    for categ in line.product_id.pos_categ_ids:
                        self.accumulate_line_data(line,vals,pos_screen_data,count,config_id,product_category_wise,categ)
           
            vals['total_items'] = len(vals['lines'])
            orders_list.append(vals)

    def accumulate_line_data(self, line, vals, pos_screen_data, count, config_id, product_category_wise, categ):
        """
            appends lines for the kitchen order in vals

            params:
            line: pos.kitchen.orderline model object
            vals:dict, order data
            pos_screen_data:pos.kitchen.screen.config model object
            count: int
            config_id:int, screen id
            product_category_wise:dict
            categ:pos.category model object

        """
        if categ and categ in pos_screen_data.pos_category_ids and not count:
            count += 1
            line_vals = {
                'note':hasattr(line, 'note') and line.note or '',
                'display_name':line.display_name,
                'id':line.id,
                'state':line.state,
                'done_line':"/pos/"+str(line.id)+"/done/orderline",
                'order_id':[line.order_id.id, line.order_id.name],
                'screen_config':pos_screen_data.id,
                'discount':line.discount,
                'qty':line.qty,
            }
            if hasattr(config_id, 'order_action') and config_id.order_action == 'order_button' and line and line.qty_added:
                line_vals['qty_added'] = line.qty_added
            if hasattr(config_id, 'order_action') and config_id.order_action == 'order_button' and line.qty_removed:
                line_vals['qty_removed'] = line.qty_removed
            product = line.read(['product_id'])
            if len(product):
                line_vals['product_id'] = list(product[0].get('product_id'))
                line_vals['product_id'][1] = line.full_product_name or line_vals['product_id'][1]
                if len(line_vals['product_id'][1].split(']')) == 2:
                    line_vals['product_id'][1] = line.full_product_name or line_vals['product_id'][1].split(']')[
                        1]
            else:
                line_vals['product_id'] = [line.product_id.id,
                                           line.full_product_name or line.product_id.name]
            if categ:
                categ_id = categ.name+'-'+str(categ.id)
                if categ_id not in product_category_wise:
                    product_category_wise[categ_id] = {line.id: line_vals}
                else:
                    product_category_wise[categ_id].update(
                        {line.id: line_vals})
            else:
                categ_id = "General"+'-'+str(0)
                if categ_id not in product_category_wise:
                    product_category_wise[categ_id] = {line.id: line_vals}
                else:
                    product_category_wise[categ_id].update(
                        {line.id: line_vals})
            vals['lines'].append(line_vals)
            vals['product_category_wise'] = product_category_wise

class PosKitchenOrderLines(models.Model):
    _name = 'pos.kitchen.orderline'
    _description = "POS Kitchen Orderline"

    order_id = fields.Many2one('pos.kitchen.order', string="Related Pos Order")
    display_name = fields.Char(string="Display Name")
    is_orderline_done = fields.Boolean(
        string="Is Orderline Done", default=False)
    is_orderline_cancel = fields.Boolean(
        string="Is Orderline Cancel", default=False)
    product_id = fields.Many2one('product.product', string="Product")
    state = fields.Selection([('cancel', "Cancel"), ('in_process', 'In Process'), (
        'done', 'Done'), ('in_queue', 'In Queue'), ('new', 'New')], string="State", default="new")
    qty = fields.Integer(string="Quantity" ,readonly=True)
    note = fields.Char(string="Note")
    previous_quantity = fields.Integer(string="Previous Quantity",default=0)
    previous_first_quantity = fields.Integer(string="Previous First Quantity",default=0)
    qty_added = fields.Integer(string="Quantities Added",default=0)
    qty_removed = fields.Integer(string="Quantities Removed",default=0)
    total_qtys = fields.Integer(string="Total Quantities",default=0)
    price_unit = fields.Float(string="Price")
    full_product_name = fields.Char(string="Full Product Name")
