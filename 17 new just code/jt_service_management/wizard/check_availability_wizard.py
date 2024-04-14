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

from odoo import fields, models, api


class CheckSPAvailabilityWizard(models.TransientModel):
    _name = "check.sp.availability.wizard"
    _description = "Check Service Product Availability"

    @api.model
    def _default_list(self):
        """
        Get the default list of items for the wizard.
        """
        res = []
        ticket_obj = self.env['crm.claim']
        incoming_shipment = self.env['stock.picking'].search([
            ('picking_type_id.code', '=', 'incoming'),
            ('state', 'not in', ('cancel', 'done'))
        ])
        ticket_id = ticket_obj.browse(self._context.get('active_id'))

        for each in ticket_id.details_ids:
            if each.product_id:
                vals = {
                    'product_id': each.product_id.id,
                    'quantity_on_hand': each.product_id.qty_available,
                    'qoh_after_so': each.product_id.qty_available - each.product_id.outgoing_qty,
                    'ordered_qty': each.quantity,
                    'virtual_available': each.product_id.virtual_available
                }

                for shipment in incoming_shipment:
                    for line in shipment.move_ids_without_package:
                        if line.product_id.id == each.product_id.id:
                            if 'eta' not in vals.keys() or (line.date_expected and vals.get('eta') > line.date_expected):
                                vals.update({'eta': line.date_expected})

                val = (0, 0, vals)
                res.append(val)

        return res

    item_line = fields.One2many('check.sp.availability.lines', 'item_id', "Item Lines", default=_default_list)


class ServiceProductsAvailabilityLines(models.TransientModel):
    _name = "check.sp.availability.lines"
    _description = "Availability Item Lines"

    item_id = fields.Many2one('check.sp.availability.wizard', 'Item Lines', readonly=True)
    product_id = fields.Many2one('product.product', "Product", readonly=True)
    quantity_on_hand = fields.Float('Quantity on Hand', readonly=True)
    qoh_after_so = fields.Float('QoH - SO', readonly=True)
    ordered_qty = fields.Float('Ordered Qty', readonly=True)
    virtual_available = fields.Float('Forecasted', readonly=True)
    eta = fields.Datetime('ETA', readonly=True)
