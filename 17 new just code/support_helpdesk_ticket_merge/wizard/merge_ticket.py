# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TicketMergeWizard(models.TransientModel):
    _name = "ticket.merge.wizard"
    _description = 'Helpdesk Ticket Merge Wizard'

    merge_ticket_line_ids = fields.One2many(
        'merge.ticket.line',
        'primary_ticket_merge_id',
        string="Merge Ticket Line",
        readonly=True,
    )
    # merge_new_ticket_line_ids = fields.One2many(
    #     'merge.ticket.line',
    #     'ticket_merge_id',
    #     string="Merge Ticket Line",
    # ) #odoo13
    #support_ticket_ids = fields.Many2many(
    #    'helpdesk.support',
    #    string="Merge Tickets",
    #)
    support_ticket_id = fields.Many2one(
        'helpdesk.support',
        string="Set as Primary Ticket",
    )
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        required=True,
    )
    team_id = fields.Many2one(
        'support.team',
        string='Support Team',
        required=True,
    )
    create_new_ticket = fields.Boolean(
        string='Create New Ticket?'
    )
    ticket_subject = fields.Char(
        string='Subject'
    )
    primary_id = fields.Many2one(
        'helpdesk.support',
        string="Primary Ticket",
    )
    merge_ids = fields.Many2many(
        'helpdesk.support',
        string="Merge Ticket",
    )
    is_sure = fields.Boolean(
        string="Are You Sure ?",
    )
    merge_reason = fields.Char(
        string="Merge Reason",
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    ) #odoo13
    email = fields.Char(
        string="Email",
        required=False
    ) #odoo13
    phone = fields.Char(
        string="Phone"
    ) #odoo13
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
    ) #odoo13
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
    ) #odoo13
    type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        copy=False,
    ) #odoo13
    subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
        copy=True,
    ) #odoo13

    @api.model
    def default_get(self, fields):
        res = super(TicketMergeWizard, self).default_get(fields)
        tecket_obj = self.env['helpdesk.support']
        ticket_ids = tecket_obj.search(
            [('id', 'in', self._context.get('active_ids'))]
        )
        ticket_line = self.env['merge.ticket.line']
        # if all([x.partner_id == ticket_ids[0].partner_id
        #         for x in ticket_ids]) or\
        #    all([x.email == ticket_ids[0].email for x in ticket_ids]) or\
        #    all([x.phone == ticket_ids[0].phone for x in ticket_ids]):
        if all([x.partner_id.commercial_partner_id in ticket_ids[0].partner_id.commercial_partner_id
                for x in ticket_ids]): #odoo13
            if 'merge_ticket_line_ids' in fields:
                for ticket in ticket_ids:
                    vals = {
                        'ticket_id': ticket.id,
                        'subject': ticket.subject,
                        'responsible_user_id': ticket.user_id.id, #odoo13
                        'partner_id': ticket.partner_id.id, #odoo13
                        'phone': ticket.partner_id.phone, #odoo13
                        'email': ticket.partner_id.email, #odoo13
                        'priority': ticket.priority, #odoo13
                        'team_id': ticket.team_id.id, #odoo13
                        'category': ticket.category, #odoo13
                        'type_ticket_id': ticket.type_ticket_id.id, #odoo13
                        'subject_type_id': ticket.subject_type_id.id, #odoo13
                    }
                    ticket_line += ticket_line.create(vals)
                    res.update({
                        'merge_ticket_line_ids': [(6, 0, ticket_line.ids)],
                        'merge_ids': [(6, 0, ticket_ids.ids)],
                        'responsible_user_id': ticket.user_id.id, #odoo13
                        'partner_id': ticket.partner_id.id, #odoo13
                        'phone': ticket.partner_id.phone, #odoo13
                        'email': ticket.partner_id.email, #odoo13
                        'priority': ticket.priority, #odoo13
                        'team_id': ticket.team_id.id, #odoo13
                        'ticket_subject': ticket.subject, #odoo13
                        'category': ticket.category, #odoo13
                        'type_ticket_id': ticket.type_ticket_id.id, #odoo13
                        'subject_type_id': ticket.subject_type_id.id, #odoo13
                    })
        else:
            raise ValidationError(_("Must be Same Partner or Email or Phone."))
        return res

    def merge_ticket_messages(self, ticket=None):
        return True

    #@api.multi
    def action_merge_ticket(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        desc = ''
        helpdesk_support_obj = self.env['helpdesk.support']
        primary_ticket = self.primary_id
        if self.primary_id:
            if self.is_sure:
                primary_ticket.write({'is_secondry': True})
                for line in self.merge_ids:
                    if line == self.primary_id:
                        pass
                    else:
                        merge_ticket = line
                        d = merge_ticket.description or ''
                        desc += '\n' + d
                        merge_ticket.write({
                        'primary_ticket_id': primary_ticket.id,
                        'is_secondry': True, 
                        'active': False,
                         })
                primary_ticket.write({
                    'description': self.primary_id.description or '' + desc,
                    'merge_reason': self.merge_reason,
                 })
                self.merge_ticket_messages() #odoo14
                # res = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
                # res = res.sudo().read()[0]
                res = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
                res['domain'] = str([('id', '=', primary_ticket.id)])
                return res
            else:
                raise ValidationError(_("Please select check box to confirm merge."))
        if self.create_new_ticket:
            add_desc = ''
            for line in self.merge_ids:
                add_desc += '\n' + (line.description or '')
            if self.is_sure: #odoo13
                new_ticket_vals = {
                    'subject': self.ticket_subject,
                    'user_id': self.responsible_user_id.id,
                    'team_id': self.team_id.id,
                    'team_leader_id': self.team_id.leader_id.id,
                    'merge_reason': self.merge_reason,
                    'description': add_desc,
                    'partner_id': self.partner_id.id, #odoo13
                    'phone': self.partner_id.phone, #odoo13
                    'email': self.partner_id.email, #odoo13 
                    'priority': self.priority, #odoo13 
                    'category': self.category, #odoo13
                    'type_ticket_id': self.type_ticket_id.id, #odoo13
                    'subject_type_id': self.subject_type_id.id, #odoo13
                }
                new_ticket = helpdesk_support_obj.create(new_ticket_vals)
                self.merge_ticket_messages(new_ticket)
                self.merge_ids.write({
                    'active': False
                    }) #odoo13
            else: #odoo13
                raise ValidationError(_("Please select check box to confirm create.")) #odoo13

class MergeTicketLine(models.TransientModel):
    _name = "merge.ticket.line"
    _description = 'Merge Ticket Line'

    ticket_id = fields.Many2one(
        'helpdesk.support',
        string="Support Ticket",
        readonly=True,
    )
    subject = fields.Text(
        string='Subject',
    )
    # ticket_merge_id = fields.Many2one(
    #     'ticket.merge.wizard',
    #     string="Merge",
    # ) #odoo13
    primary_ticket_merge_id = fields.Many2one(
        'ticket.merge.wizard',
        string="Merge",
    )

    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
    ) #odoo13
    team_id = fields.Many2one(
        'support.team',
        string='Support Team',
    ) #odoo13
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer',
    ) #odoo13
    phone = fields.Char(
        string='Phone',
    ) #odoo13
    email = fields.Char(
        string='Customer Email',
    ) #odoo13
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
    ) #odoo13
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
    ) #odoo13
    type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        copy=False,
    ) #odoo13
    subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
        copy=True,
    ) #odoo13

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
