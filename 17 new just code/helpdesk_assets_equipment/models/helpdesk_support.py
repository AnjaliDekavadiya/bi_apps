# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class HelpdeskSupport(models.Model):

    _inherit = 'helpdesk.support'
    
#    @api.multi odoo13
    def open_equipment_request_from_ticket(self):
        self.ensure_one()
        # action = self.env.ref('helpdesk_assets_equipment.action_helpdesk_assets_equipment').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('helpdesk_assets_equipment.action_helpdesk_assets_equipment')
        action['domain'] = [('helpdesk_support_id', '=', self.id)]
        return action

#    @api.multi odoo13
    def open_equipment_from_ticket(self):
        self.ensure_one()
        # action = self.env.ref('maintenance.hr_equipment_action').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('maintenance.hr_equipment_action')
        helpdesk_assets_equipment_id = self.env['helpdesk.assets.equipment'].search([('helpdesk_support_id', '=', self.id)])
        equipment_ids = helpdesk_assets_equipment_id.mapped('helpdesk_assets_equipment_line.maintenance_equipment_id')
        # action['domain'] = [('id', '=', equipment_ids.ids)]
        action['domain'] = [('id', 'in', equipment_ids.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
