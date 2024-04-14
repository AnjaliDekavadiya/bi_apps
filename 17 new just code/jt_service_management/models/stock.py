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


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_type_code = fields.Selection(related='picking_id.picking_type_code', string="Picking Type Code")


class StockMove(models.Model):
    _inherit = 'stock.move'

    parts_line_id = fields.Many2one('service.parts.info.one', 'Parts Order Line', ondelete='set null', readonly=True)
    is_service_move = fields.Boolean('Is Service Move', default=False)
    is_rfq_created = fields.Boolean('Is RFQ Created', default=False)
    picking_type_code = fields.Selection(related='picking_id.picking_type_code', string="Picking Type Code")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ticket_id = fields.Many2one('crm.claim', string='Diagnosis Details')
    is_related_to_service = fields.Boolean(string='Service Picking')

    def action_done(self):
        """
        This function changes spare parts status to Received when validating picking of the ticket.
        :return: Received status of spare parts.
        """
        res = super(StockPicking, self).action_done()
        for detail_id in self.ticket_id.details_ids:
            detail_id.status = 'received'
        return res


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_dxb_stock = fields.Boolean("DXB Stock", copy=False, default=False)
