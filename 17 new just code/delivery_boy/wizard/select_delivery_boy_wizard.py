# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, _

class SelectDeliveryBoy(models.TransientModel):
    _name = 'wizard.select.delivery.boy'
    _description = 'wizard select delivery boy model'

   
    def check_domain(self):
        deliveryBoyConfig_obj=self.env['delivery.boy.config'].search([],limit=1)

        if deliveryBoyConfig_obj.authentication_type == 'employee':
            domain=[('is_delivery_boy','=',True),('employee','=',True)]
        else:
            domain=[('is_delivery_boy','=',True),('employee','=',False)]
        return domain

    delivery_boy_partner_id = fields.Many2one(comodel_name="res.partner", context={'name_get_override':True},domain=check_domain)
    stock_picking_id = fields.Many2one(comodel_name="stock.picking")

    def _create_delivery_boy_picking(self):
        if self.stock_picking_id.delivery_boy_picking_id:
            self.stock_picking_id.delivery_boy_picking_id.picking_state = 'cancel'
        vals = {
        'assigned_date':fields.Datetime.now(),
        'picking_id': self.stock_picking_id.id,
        'partner_id': self.delivery_boy_partner_id.id,
        }
        return self.env['delivery.boy.pickings'].create(vals)

    def action_assign_delivery_boy(self):
        db_picking = self._create_delivery_boy_picking()
        self.stock_picking_id.delivery_boy_partner_id = self.delivery_boy_partner_id.id
        self.stock_picking_id.delivery_boy_picking_id = db_picking.id

        msg = _("Delivery boy Picking with Reference Id %s has been created.")%(db_picking.name)
        partial_id = self.env['msg.wizard'].create({'text': msg})
        db_picking._pushNotification('p_assigned',db_picking.partner_id.id)
        return {
        'name': "Message",
        'view_mode': 'form',
        'view_id': False,
        'res_model': 'msg.wizard',
        'res_id': partial_id.id,
        'type': 'ir.actions.act_window',
        'nodestroy': True,
        'target': 'new',
        }
