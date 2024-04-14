# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class helpdeskInvoice(models.Model):
    _inherit = 'account.move'

    sh_ticket_ids = fields.Many2many("helpdesk.ticket",'sh_account_move_helpdesk_ticket_rel', string="Tickets")
    ticket_count = fields.Integer(
        'Ticket', compute='_compute_ticket_count')

    def action_create_ticket(self):
        context = {}
        if self.partner_id:
            context.update({
                'default_partner_id': self.partner_id.id,
            })
        if self.user_id:
            context.update({
                'default_user_id': self.user_id.id,
            })
        if self:
            context.update({
                'default_sh_invoice_ids': [(6, 0, self.ids)],
            })
        if self.invoice_line_ids:
            products = []
            for line in self.invoice_line_ids:
                if line.product_id and line.product_id.id not in products:
                    products.append(line.product_id.id)
            context.update({
                'default_product_ids': [(6, 0, products)]
            })
        return{
            'name': 'Helpdesk Ticket',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'form',
            'context': context,
            'target': 'self'
        }

    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = 0
            tickets = self.env['helpdesk.ticket'].search(
                [('sh_invoice_ids', 'in', record.ids)], limit=None)
            record.ticket_count = len(tickets.ids)

    def ticket_counts(self):
        self.ensure_one()
        tickets = self.env['helpdesk.ticket'].sudo().search(
            [('sh_invoice_ids', 'in', self.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "helpdesk.helpdesk_ticket_action_main_my")
        if len(tickets) > 1:
            action['domain'] = [('id', 'in', tickets.ids)]
        elif len(tickets) == 1:
            form_view = [
                (self.env.ref('helpdesk.helpdesk_ticket_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tickets.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
