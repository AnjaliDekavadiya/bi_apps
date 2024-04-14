# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    is_create_ticket = fields.Boolean(
        string="Is Create Ticket",
        copy = False
    )

#    @api.multi odoo13
    def action_open_helpdesk_ticket(self):
        self.ensure_one()
        ticket_ids = self.env['helpdesk.support'].search([('lead_id', '=', self.id)])
        action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support').sudo().read()[0]
        action['domain'] = [('id', 'in', ticket_ids.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
