# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def custom_action_cloth_request(self):
        cloth_request_ids = self.env['cloth.request.details'].sudo().search([('lead_id', 'in', self.ids)])
        #action = self.env.ref('cloth_tailor_management_odoo.action_cloth_request_details').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_management_odoo.action_cloth_request_details')
        if len(cloth_request_ids) > 1:
            action['domain'] = [('id', 'in', cloth_request_ids.ids)]
        elif len(cloth_request_ids) == 1:
            form_view = [(self.env.ref('cloth_tailor_management_odoo.cloth_request_details_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = cloth_request_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        if len(self) == 1:
            context = {
                'default_partner_id': self.partner_id.id,
                'default_lead_id': self.id,
            }
            action['context'] = context
        return action