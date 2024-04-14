# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class ServiceCenterDOReport(models.Model):

    _name = 'service.delivery.reference.report'
    _description = "Service Delivery Reference Report"

    name = fields.Char("Delivery Order Reference Number")
    partner_id = fields.Many2one("res.partner", string="Customer")
    date = fields.Datetime("Date")
    stage = fields.Selection([('collected', 'Collected')], "Status")
    ticket_ids = fields.Many2many('crm.claim', 'rel_ticket_report', 'ticket_id', 'report_id',
                                  string="Tickets")
    printed_by = fields.Many2one('res.users', 'Printed By')
    printed_time = fields.Datetime('Printed Time')

    def get_attention_data(self, tickets):
        data = {}
        for ticket in tickets:
            if not ticket.partner_id.is_company and ticket.partner_id.parent_id:
                data.update({
                    'name': ticket.partner_id.name,
                    'email': ticket.partner_id.email,
                    'mobile': ticket.partner_id.mobile
                })
                break
        return data

    def get_tickets(self, tickets):
        details_vals = []
        for ticket in tickets:
            received_date_formated = datetime.strptime(str(ticket.date), '%Y-%m-%d %H:%M:%S')
            received_date = received_date_formated.strftime('%d-%b-%Y')
            stage = 'New' if ticket.stage == 'new' else 'Collected' if ticket.stage == 'ready_for_collection' else ''
            
            details_vals.append(
                {
                    'ticket_no': ticket.name,
                    'product_name': ticket.product_id.name,
                    'product_code': ticket.product_id.default_code,
                    'serial_no': ticket.serial_number,
                    'received_date': received_date,
                    'action_take': ticket.action_type_id.name,
                    'action_desc': ticket.cause,
                    'status': stage,
                    'categ_id': ticket.categ_id.name,
                    'description': ticket.description,
                    'sale_id': ticket.sale_id.name
                })
        return details_vals


class PrintReportWizard(models.TransientModel):
    _name = 'print.report.wizard'
    _description = "Print Report wizard"

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, domain="[('is_company', '=', True)]")
    report_type = fields.Selection([('receipt', 'Receipt'), ('delivery', 'Delivery')], string='Report Type',
                                   required=True)
    tickets = fields.Many2many('crm.claim', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    user_id = fields.Many2one("res.users", string="User")
    do_ref = fields.Char("Do Ref")

    def print_do_report(self):
        self.ensure_one()
        if self.report_type == 'delivery':
            seq_obj = self.env['ir.sequence'].sudo()
            do_reference = seq_obj.next_by_code('crm.claim.do') or _('New')
            self.do_ref = do_reference
            ticket_ids = self.tickets.ids if self.tickets else []
            self.env['service.delivery.reference.report'].create({
                'partner_id': self.partner_id.id,
                'name': self.do_ref,
                'stage': 'collected',
                'date': datetime.today().date(),
                'printed_by': self._uid,
                'printed_time': datetime.now(),
                'ticket_ids': [(6, 0, ticket_ids)] if ticket_ids else []
            })
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        report = self.env.ref('jt_service_management.action_print_report').report_action(self, data=data)

        return report

    def get_tickets(self, tickets):
        details_vals = []
        for ticket in tickets:
            received_date_formated = datetime.strptime(str(ticket.date), '%Y-%m-%d %H:%M:%S')
            received_date = received_date_formated.strftime('%d-%b-%Y')
            stage = 'New' if ticket.stage == 'new' else 'Collected' if ticket.stage == 'ready_for_collection' else ''

            details_vals.append(
                {
                    'ticket_no': ticket.name,
                    'product_name': ticket.product_id.name,
                    'product_code': ticket.product_id.default_code,
                    'serial_no': ticket.serial_number,
                    'received_date': received_date,
                    'action_take': ticket.action_type_id.name,
                    'action_desc': ticket.cause,
                    'status': stage,
                    'categ_id': ticket.categ_id.name,
                    'description': ticket.description,
                    'sale_id': ticket.sale_id.name
                })
            if self.report_type == 'delivery':
                ticket.with_context(from_report=True).write({'stage': 'collected', 'do_reference': self.do_ref})
            self.tickets = False
        return details_vals

    @api.onchange('partner_id')
    def onchange_customer(self):
        report_type = self.report_type
        self.tickets = False
        customer = self.partner_id
        all_child_partners = self.env['res.partner'].search([('parent_id', '=', customer.id)]).ids
        all_child_partners.append(customer.id)
        ticket_ids = []
        if report_type == 'receipt':
            ticket_ids = self.env['crm.claim'].search(
                [('partner_id', 'in', all_child_partners), ('stage', '=', 'new')]).ids
        elif report_type == 'delivery':
            ticket_ids = self.env['crm.claim'].search([('partner_id', 'in', all_child_partners),
                                                       ('stage', '=', 'ready_for_collection')]).ids

        res = {}
        res['domain'] = {'tickets': [('id', 'in', ticket_ids)]}
        return res

    def get_attention_data(self, tickets):
        data = {}
        for ticket in tickets:
            if not ticket.partner_id.is_company and ticket.partner_id.parent_id:
                data.update({
                    'name': ticket.partner_id.name,
                    'email': ticket.partner_id.email,
                    'mobile': ticket.partner_id.mobile
                })
                break
        return data

    @api.onchange('report_type')
    def onchange_report_type(self):
        self.tickets = False
        self.partner_id = False
        all_parent_partner_ids = []
        res = {}
        report_type = self.report_type
        if report_type == 'receipt':
            all_partner_dict = self.env['crm.claim'].search_read([('stage', '=', 'new')], ['partner_id'])
            all_partner_dup_ids = [x['partner_id'][0] for x in all_partner_dict]
            all_partner_ids = self.env['res.partner'].search([('id', 'in', all_partner_dup_ids)])
            all_parent_partner_ids = [all_partner_id.parent_id.id if all_partner_id.parent_id else all_partner_id.id
                                      for all_partner_id in all_partner_ids]

        elif report_type == 'delivery':
            all_partner_dict = self.env['crm.claim'].search_read([('stage', '=', 'ready_for_collection')],
                                                                 ['partner_id'])
            all_partner_dup_ids = [x['partner_id'][0] for x in all_partner_dict]
            all_partner_ids = self.env['res.partner'].search([('id', 'in', all_partner_dup_ids)])
            all_parent_partner_ids = [all_partner_id.parent_id.id if all_partner_id.parent_id else all_partner_id.id
                                      for all_partner_id in all_partner_ids]

        res['domain'] = {'partner_id': [('id', 'in', all_parent_partner_ids)]}
        return res


class PrintReport(models.AbstractModel):
    _name = 'report.jt_service_management.view_print_wizard_report'
    _description = "Print Report"

    def _get_info(self, data):
        partner_id = data['form'].get('partner_id')[0]
        partner = self.env['res.partner'].browse(partner_id)
        data = {'report_type': data['form'].get('report_type'),
                'partner': partner}
        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        context = self.env.context
        if not context.get('active_model') or not context.get('active_id'):
            raise UserError(_("Form content is missing, this report \
            cannot be printed."))

        model = context.get('active_model')
        docs = self.env[model].browse(context.get('active_id'))

        docargs = {
            'doc_ids': docids,
            'docs': docs,
            'get_info': self._get_info,
        }
        return docargs
