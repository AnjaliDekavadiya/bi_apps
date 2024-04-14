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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SparesLocation(models.TransientModel):

    _name = 'spares.location'
    _description = "Spares Location"

    location_source_id = fields.Many2one('stock.location', string='Default Spare Parts Location', required=True)
    location_dest_id = fields.Many2one('stock.location', string='Default Service Center Location', required=True)

    @api.model
    def default_get(self, fields):
        res = super(SparesLocation, self).default_get(fields)
        user_service_center = self.env.user.service_center_id
        if user_service_center:
            res.update({
                'location_source_id': user_service_center.source_location_id.id,
                'location_dest_id': user_service_center.destination_location_id.id
            })
        else:
            service_center = self.env['service.center'].search([], limit=1)
            if service_center:
                res.update({
                    'location_source_id': service_center.source_location_id.id,
                    'location_dest_id': service_center.destination_location_id.id
                })
            else:
                _logger.info("Service center is not configured!")
        return res

    def create_internal_transfer(self):
        context = self.env.context
        ticket_id = context.get('ticket_id', False)
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        picking_type = self.env['stock.picking.type']

        if not ticket_id:
            raise UserError(_("Ticket ID is missing!"))

        ticket = self.env['crm.claim'].browse(ticket_id)

        if not ticket.service_engineer_id.service_center_id:
            raise UserError(_("Service Center is not attached to the User record. Please contact the administrator or service manager."))

        if not ticket.details_ids:
            raise UserError(_('Please enter at least one spare part or service product detail in the list'))

        if not ticket.resolution:
            raise UserError(_('Please enter the diagnosis description which is mandatory!'))

        source_location_id = ticket.service_engineer_id.service_center_id.source_location_id.id
        destination_location_id = ticket.service_engineer_id.service_center_id.destination_location_id.id

        picking_type = picking_type.search([('default_location_src_id', '=', source_location_id),
                                            ('default_location_dest_id', '=', destination_location_id)], limit=1)

        if not picking_type:
            raise UserError(_('Picking Type not found!'))

        picking = picking_obj.create({
            'partner_id': False,
            'picking_type_id': picking_type.id,
            'origin': ticket.name,
            'location_id': self.location_source_id.id,
            'location_dest_id': self.location_dest_id.id,
            'is_related_to_service': True,
            'ticket_id': ticket.id
        })

        for val in ticket.details_ids:
            if val.product_id.type != 'service' and val.status == 'new':
                move_obj.create({
                    'product_id': val.product_id.id,
                    'product_uom': val.uom_id.id,
                    'name': val.product_id.name,
                    'location_id': self.location_source_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'picking_type_id': picking_type.id,
                    'product_uom_qty': val.quantity,
                    'picking_id': picking.id,
                    'parts_line_id': val.id,
                    'is_service_move': True,
                })
                val.status = 'requested'
                picking.action_confirm()

        ticket.parts_confirmed = True
