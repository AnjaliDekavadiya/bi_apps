# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class HrExpense(models.Model):

    _inherit = 'hr.expense'

    custom_helpdesk_suppor_id = fields.Many2many(
        'helpdesk.support',
        string='Support Tickets',
    )
    ticket_count = fields.Integer(
        string='# Ticket Count',
        compute='_compute_ticket_count', 
        readonly=True, 
        default=0
    )

    @api.depends()
    def _compute_ticket_count(self):
        for expense in self:
            helpdesk_support_ids = expense.mapped('custom_helpdesk_suppor_id')
            expense.ticket_count = len(helpdesk_support_ids.ids)
#       unnecessary code odoo13
#        helpdesk_support = self.env['helpdesk.support']
#        tickets_id = []
#        for tickets in self:
#            tickets_support_id = tickets.custom_helpdesk_suppor_id
#            tickets_id = [i['id'] for i in tickets_support_id]
#            tickets.ticket_count = len(tickets_id)
            
#    @api.multi odoo13
    def open_tickets_view(self):
        self.ensure_one()
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        helpdesk_support_ids = self.mapped('custom_helpdesk_suppor_id')
#       unnecessary code odoo13        
#        tickets_id = []
#        for tickets in self:
#            tickets_support_id = tickets.custom_helpdesk_suppor_id
#            tickets_id = [i['id'] for i in tickets_support_id]
        action['domain'] = [('id', 'in', helpdesk_support_ids.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
