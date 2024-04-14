# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class MaintenanceEquipment(models.Model):

    _inherit = 'maintenance.equipment'

#    @api.multi odoo13
    def open_equipment(self):
        self.ensure_one()
        #action = self.env.ref('helpdesk_assets_equipment.action_helpdesk_assets_equipment').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('helpdesk_assets_equipment.action_helpdesk_assets_equipment')
        action['domain'] = [('helpdesk_assets_equipment_line.maintenance_equipment_id', '=', self.id)]
        return action

#    @api.multi odoo13
    def open_support_ticket(self):
        self.ensure_one()
        #action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        helpdesk_assets_equipment_id = self.env['helpdesk.assets.equipment'].search([('helpdesk_assets_equipment_line.maintenance_equipment_id', '=', self.id)])
        helpdesk_support_id = helpdesk_assets_equipment_id.mapped('helpdesk_support_id')
        # action['domain'] = [('id', '=', helpdesk_support_id.ids)]
        action['domain'] = [('id', 'in', helpdesk_support_id.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



