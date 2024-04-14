# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-Today Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Anil R. Kesariya(<http://www.jupical.com>)
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
from odoo import api, models, fields, _


class StockProductionlot(models.Model):
    _inherit = 'stock.production.lot'

    po_line_id = fields.Many2one("purchase.order.line", "Purchase Line")
    price_unit = fields.Float("Unit Price")
    total_cost = fields.Float(
        string="Total Cost", compute='_compute_product_total_cost', store=True)

    @api.depends('product_qty', 'price_unit')
    def _compute_product_total_cost(self):
        for rec in self:
            rec.total_cost = rec.price_unit * rec.product_qty

