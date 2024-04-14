# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class HelpdeskSupport(models.Model):
    
    _inherit = 'helpdesk.support'

    custom_parent_id = fields.Many2one(
        'helpdesk.support',
        string='Parent Ticket',
        copy=False,

    )
    custom_child_id = fields.One2many(
        'helpdesk.support',
        'custom_parent_id',
        string='Child Ticket',
        copy=False,
    )
    custom_child_id_counter = fields.Integer(
        string='Counter',
        compute='_compute_child_id',
    )

    @api.depends()
    def _compute_child_id(self):
        for ticket in self:
            ticket.custom_child_id_counter = len(ticket.custom_child_id)

    # @api.multi #odoo13
    def open_child_ticket(self):
        self.ensure_one()
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        child_ids = self.custom_child_id.mapped('id')
        action['domain'] = [('id', 'in', child_ids)]
        action['context'] = {'default_custom_parent_id' : self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



            
    