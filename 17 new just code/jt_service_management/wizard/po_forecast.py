# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api, _


class PurchaseForecastWizard(models.TransientModel):

    _name = "purchase.forecast.wizard"
    _description = "Purchase Forecast Qty Wizard"

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    partner_id = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', True)])
    date_order = fields.Date("Date", default=fields.Date.context_today)

    def create_rfq(self):
        """
        This function creates RFQ form tree view of stock.move(Purchase -> Control -> Incoming Product).
        :return: RFQ.
        """
        stock_move_obj = self.env['stock.move']
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        move_ids = self._context.get('active_ids')
        source_document = ''
        partner_id = self.partner_id.id

        for move_id in move_ids:
            old_purchase = purchase_order_obj.search([('partner_id', '=', partner_id),
                                                      ('state', '=', 'draft')])

            move = stock_move_obj.browse(move_id)
            qty_to_purchase = move.product_uom_qty

            purchase_order_lines = {
                'product_id': move.product_id.id,
                'product_qty': qty_to_purchase,
                'product_uom': move.product_uom.id,
                'price_unit': move.product_id.standard_price,
                'name': move.product_id.name,
                'date_planned': move.date_expected,
            }

            if move.origin:
                source_document = source_document + move.origin + ', '

            order_line = []
            order_line.append((0, 0, purchase_order_lines))

            if old_purchase:
                purchase_line = purchase_order_line_obj.search([('order_id', '=', old_purchase.id),
                                                                ('product_id', '=', move.product_id.id)], limit=1)
                if purchase_line:
                    purchase_line_qty = purchase_line.product_qty
                    purchase_line.product_qty = qty_to_purchase + purchase_line_qty
                    move.is_rfq_created = True
                else:
                    old_purchase.order_line = order_line
                    move.is_rfq_created = True
                move.state = 'draft'
                move.rfq_ref = old_purchase.id
            else:
                po = purchase_order_obj.create({
                    'partner_id': self.partner_id.id,
                    'date_order': self.date_order,
                    'date_planned': self.date_order,
                    'order_line': order_line,
                    'origin': source_document
                })
                move.is_rfq_created = True
                move.state = 'draft'
                move.rfq_ref = po.id if po else False

        return True
