# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    lead_id = fields.Many2one(
        'crm.lead',
        string="CRM Lead",
        copy = False,
        readonly=True,
    )
    is_lead = fields.Boolean(
        string="Is Lead Ticket",
        readonly=True,
        copy = False
    )
    lead_user_id = fields.Many2one(
        'res.users',
        string="Lead Responsible",
        readonly=True,
        copy = False
    )

    # unused code odoo13
    # @api.multi
    # def action_open_crm_lead(self):
    #     self.ensure_one()
    #     action = self.env.ref('crm.crm_lead_opportunities_tree_view').sudo().read()[0]
    #     action['domain'] = [('id', 'in', self.lead_id.ids)]
    #     return action
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
