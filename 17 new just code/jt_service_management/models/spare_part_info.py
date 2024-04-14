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

from odoo import api, fields, models, _


class SparePartInfoOne(models.Model):

    _name = 'service.parts.info.one'
    _description = "Spare Part Info"

    status_of_wt = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')],
        string='Status of WT', compute='_compute_status_of_wt', store=True)
    min_date = fields.Datetime('Scheduled Date')
    rfq_qty = fields.Integer('RFQ Qty', compute='_compute_rfq_po_so_qty')
    po_qty = fields.Integer('PO Qty', compute='_compute_rfq_po_so_qty')
    so_qty = fields.Integer('SO Qty', compute='_compute_rfq_po_so_qty')
    product_code = fields.Char("Product Code", related='product_id.default_code', store=True)
    prod_name = fields.Char("Name", store=True) #, related="product_id.name",
    new_part_id = fields.Many2one('crm.claim', string='Diagnosis Details')
    product_id = fields.Many2one('product.product', string='Part', required=True)
    description = fields.Char(string='Description', required=True)
    uom_id = fields.Many2one('uom.uom', string='UOM', required=True)
    quantity = fields.Float(string='Qty', default=1.00)
    price_unit = fields.Float(string='Unit Price')
    sub_total = fields.Float(string='Sub Total', compute='_compute_sub_total', store=True)
    is_requested = fields.Boolean('Requested')
    move_ids = fields.One2many('stock.move', 'parts_line_id', string='Parts Move', readonly=True, copy=False, store=True)
    status = fields.Selection([('new', 'New'), ('requested', 'Requested'), ('received', 'Received')],
                              string='State', default='new')
    quote_state = fields.Selection(related='new_part_id.quote_state')
    stage = fields.Selection(related='new_part_id.stage')

    @api.depends('move_ids', 'move_ids.state')
    def _compute_status_of_wt(self):
        for part in self:
            for move in part.move_ids:
                part.status_of_wt = move.state
                if move.picking_id:
                    part.min_date = move.picking_id.scheduled_date

    def _compute_rfq_po_so_qty(self):
        for part in self:
            rfqs = self.env['purchase.order.line'].search([
                ('order_id.state', 'in', ('draft', 'sent')),
                ('product_id', '=', part.product_id.id)])
            rfq_qty = sum(rfq.product_qty for rfq in rfqs)
            part.rfq_qty = rfq_qty

            pos = self.env['purchase.order.line'].search([
                ('order_id.state', 'in', ('purchase', 'done')),
                ('product_id', '=', part.product_id.id)])
            pos_qty = sum(po.product_qty for po in pos)
            part.po_qty = pos_qty

            sos = self.env['sale.order.line'].search([
                ('order_id.state', 'in', ('sale', 'done')),
                ('product_id', '=', part.product_id.id)])
            sos_qty = sum(so.product_uom_qty for so in sos)
            part.so_qty = sos_qty

    @api.onchange('quantity')
    def _onchange_quantity(self):
        """
        This function return warning if quantity of spare part is less than 1.
        :return: Warning if spare part quantity less than one.
        """
        if self.quantity < 1:
            self.quantity = 1
            return {
                'warning': {'title': _('Error'), 'message': _('Quantity must be more than 1'),},
            }

    @api.depends('quantity', 'price_unit')
    def _compute_sub_total(self):
        """
        This function updates subtotal of all spare parts.
        :return: subtotal
        """
        for rec in self:
            rec.sub_total = rec.quantity * rec.price_unit

    @api.onchange('product_id')
    def _onchange_product(self):
        """
        This function adds product description, uom and price when change or add product inside spare part.
        :return: product details
        """
        if self.product_id:
            product = self.product_id
            self.description = product.name
            self.uom_id = product.uom_id.id
            self.price_unit = product.list_price
