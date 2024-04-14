# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class HelpdeskSupport(models.Model):
    _inherit = "helpdesk.support"
    
    primary_ticket_id = fields.Many2one(
        'helpdesk.support',
        string="Primary Merge Ticket",
    )
    merge_ticket_ids = fields.One2many(
        'helpdesk.support',
        'primary_ticket_id',
        string="Secondary Merge Tickets",
    )
    is_secondry = fields.Boolean(
        string="Is Secondry ?",
        default=False,
    )
    merge_reason = fields.Char(
        string="Merge Reason",
    )

    #@api.multi
    def show_secondry_ticket(self):
        self.ensure_one()
        secondry = self.search([('primary_ticket_id', '=', self.id), ('active', '!=', True)])
        # res = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        res['domain'] = str([('id', 'in', secondry.ids), ('active', '!=', True)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
