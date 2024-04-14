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

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    ticket_ids = fields.One2many('crm.claim', 'sale_id', 'Ticket References', copy=False)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.ticket_ids.quote_state = 'order_confirmed'
        return res

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     for order in self:
    #         if order.state == 'sale':
    #             tickets = self.env['crm.claim'].search([('sale_id', '=', order.id)])
    #             if tickets:
    #                 for ticket in tickets:
    #                     ticket.quote_state = 'order_confirmed'
    #                 if order.picking_ids:
    #                     service_center = self.env['service.center'].search([], limit=1)
    #                     if service_center and service_center.picking_type_id:
    #                         for picking in order.picking_ids:
    #                             picking.picking_type_id = service_center.picking_type_id.id
    #     return res


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    group = fields.Char('Group')