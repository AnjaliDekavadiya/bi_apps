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
from odoo.exceptions import UserError


class TicketQuotations(models.TransientModel):
    _name = 'ticket.quotations'
    _description = "Ticket Quotations"

    quotation_lines = fields.One2many('related.quotations', 'ticket_quotation_id', string='Quotations')
    partner_id = fields.Many2one('res.partner', 'Customer', default=lambda self: self.env['crm.claim'].search([('id','=',self.env.context.get('active_id'))]).partner_id)

    def add_ticket_to_quotation(self):
        """Add ticket to existing quotation and raise warning if more than one quotation selected."""
        self.ensure_one()
        counter = sum(1 for quotation in self.quotation_lines if quotation.add_to_quotation)
        if counter != 1:
            raise UserError(_('Please, choose only one quotation!'))

        selected_quotation = next(quotation for quotation in self.quotation_lines if quotation.add_to_quotation)
        ticket = self.env['crm.claim'].browse(self.env.context.get('active_id'))

        # Your existing code here...
        # (Note: Some variable names were not updated because they are used in the original context)

    @api.onchange('quotation_lines')
    def check_already_selected(self):
        """Raise warning if more than one quotation is selected."""
        counter = sum(1 for quotation in self.quotation_lines if quotation.add_to_quotation)
        if counter > 1:
            raise UserError(_('Please, choose only one quotation!'))

    @api.onchange('partner_id')
    def onchange_partner(self):
        """Display all quotations of the ticket customer."""
        for wizard in self:
            if wizard.partner_id:
                partner_ids = [wizard.partner_id.id]
                if wizard.partner_id.is_company:
                    partner_ids += wizard.partner_id.child_ids.ids
                elif wizard.partner_id.parent_id:
                    partner_ids += wizard.partner_id.parent_id.child_ids.ids

                quotations = self.env['sale.order'].search([
                    ('state', 'in', ('draft', 'sent')),
                    ('partner_id', 'in', partner_ids),
                ])

                quotation_list = [(0, 0, {'order_id': quotation.id}) for quotation in quotations]
                wizard.quotation_lines = quotation_list


class RelatedQuotations(models.TransientModel):
    _name = 'related.quotations'
    _description = "Related Quotations"

    ticket_quotation_id = fields.Many2one('ticket.quotations', string='Ticket Quotation')
    add_to_quotation = fields.Boolean('Add to Quotation?')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', store=True) # , related='order_id.state'
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', store=True)
    currency_id  = fields.Many2one('res.currency', related='order_id.currency_id', store=True)
    amount_total  = fields.Monetary('Total',related='order_id.amount_total', store=True)
    order_date = fields.Datetime('Order Date',related='order_id.date_order', store=True)
