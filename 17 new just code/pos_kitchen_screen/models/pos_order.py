# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
import datetime

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_orderline_done = fields.Boolean(
        string="Is Orderline Done", default=False)
    qty_added = fields.Integer(string="Quantities Added",default=0)
    qty_removed = fields.Integer(string="Quantities Removed",default=0)
    is_orderline_cancel = fields.Boolean(
        string="Is Orderline Cancel", default=False)
    
class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_progress = fields.Selection([('cancel', "Cancel"), ('pending', 'Pending'), (
        'done', 'Done'), ('partially_done', 'Partially Done'), ('new', 'New')], string="Order Progress",readonly=True)
    screen_progress = fields.Text(string="Screen Progress",readonly=True)
    kitchen_order_name = fields.Char(string="Kitchen Order",readonly=True)
    cancellation_reason = fields.Char(string="Cancellation Reason",readonly=True)
    is_state_updated = fields.Boolean(string="Is state Updated")
    out_of_stock_products = fields.One2many(
        'product.product', 'related_order', string="Out Of Stock Products")
    kitchen_screen_id = fields.Many2one('pos.kitchen.screen.config', string="Pos Kitchen Screen",readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(PosOrder, self).create(vals_list)
        self.env['pos.session']._notify_changes_in_kitchen(records,False, records._name)
        return records
    
    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        self.env['pos.session']._notify_changes_in_kitchen(self,False, self._name)
        return res
    
    @api.model
    def get_token_number(self):
        """
            to create/send token number of order
            returns string of token
        """
        token = ''
        sequence_date_wise = self.env['token.perday'].search([], limit=1)
        if len(sequence_date_wise) == 0:
            self.env['token.perday'].search([]).unlink()
            sequence_date_wise = self.env['token.perday'].create({
                'name': "token"+datetime.date.today().strftime("%Y-%m-%d")
            })
        token = sequence_date_wise.sequence_id._next()
        return token

    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        session = self.env['pos.session'].sudo().browse(
            ui_order.get('pos_session_id'))
        if(hasattr(session.config_id, 'order_action') and session.config_id.order_action != 'order_button') or not hasattr(session.config_id, 'order_action'):
            pos_screen_data = self.env['pos.kitchen.screen.config'].search(
                        [("pos_config_ids", 'in', session.config_id.id)])
            for data in pos_screen_data.ids:
                fields_return.update({
                    'kitchen_order_name': ui_order.get('token_no'),
                    'order_progress': 'pending' if session.config_id.auto_accept else 'new',
                    'kitchen_screen_id': data
                })
            if(hasattr(session.config_id, 'order_action')):
                fields_return.update({
                    'is_kitchen_order': ui_order.get('is_kitchen_order')})
        return fields_return
    
    @api.model
    def fetch_updated_orders(self, config, order_ref):
        """
            updated orders like time,status etc
            
            params:
            config : int, pos config id
            order_ref:string , order reference

            returns dict of updations
        """
        config_id = self.env['pos.config'].browse(config)
        order = False
        result = {
            'orders': {},
            'ref_wise_token': {},
            'ref_wise_progress': {},
            'time': False,
            'updated_state': False
        }
        orders = []
        if config_id:
            if hasattr(config_id, 'order_action') and config_id.order_action == 'order_button':
                orders = self.env['pos.kitchen.order'].search([('date_order', '>=', datetime.date.today(
                )), ('config_id', '=', config_id.id), ('is_state_updated', '=', True)])
                order = self.env['pos.kitchen.order'].search(
                    [('pos_reference', 'in', order_ref)])
            else:
                orders = self.env['pos.order'].search([('date_order', '>=', datetime.date.today(
                )), ('config_id', '=', config_id.id), ('is_state_updated', '=', True)])
                order = self.env['pos.order'].search(
                    [('pos_reference', 'in', order_ref)])
        if orders:
            time_obj = datetime.datetime.now()
            current_time = time_obj.strftime("%H:%M:%S")
            result['time'] = current_time
            for order in orders:
                result['orders'][order.kitchen_order_name] = [
                    order.order_progress, order.name]
                order.is_state_updated = False
        if order:
            for obj in order:
                result['ref_wise_progress'][obj.pos_reference] = [
                    obj.order_progress, obj.kitchen_order_name]
        return result

    @api.model
    def update_order_progress(self, data):
        """
            updates progress of orders
            returns list of orders 
        """
        order_progresses = []
        if len(data):
            int_list = [int(i) for i in data]
            orders = self.browse(int_list)
            order_progresses = orders.read(['order_progress'])
        return order_progresses