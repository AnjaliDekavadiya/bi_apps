# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from random import choice
from string import digits
from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class ParkingMembership(models.Model):

    _name = 'sh.parking.membership'
    _description = 'Parking Membership'
    name = fields.Char(string="Membership Name")
    partner_id = fields.Many2one(comodel_name="res.partner",string="Member Name", 
        required=True, domain=[('sh_is_memeber','=',True)])
    phone = fields.Char(string="Phone no")
    email = fields.Char(string='Email', required=True)
    barcode = fields.Char(
        string="Card No.", help="ID used for Member identification.", copy=False)
    sh_member_amount = fields.Float(string='Amount', required=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    sh_invoice_count = fields.Integer(
        string="Invoices", compute='compute_count_invoices', default=0)
    sh_member_amount_remaining = fields.Integer(
        string="Remaining Amount", default=lambda self: self.sh_member_amount)
    sh_create_record_boolean = fields.Boolean(
        string='sh_create_record_boolean', default=False)
    _sql_constraints = [
        ('barcode_uniq', 'unique (barcode)',
         "The Badge ID must be unique, this one is already assigned to another Member.")
    ]

    @api.model
    def create(self, vals):
        vals['sh_create_record_boolean'] = True
        result = super(ParkingMembership, self).create(vals)
        return result

    def generate_random_barcode_member(self):
        for member in self:
            member.barcode = '041'+"".join(choice(digits) for i in range(9))

    @api.onchange('email')
    def onchange_validate_mail(self):
        self.ensure_one()
        if self.email:
            match_var = re.match(
                '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match_var == None:
                raise ValidationError('Not a valid E-mail ID')

    @api.onchange('partner_id')
    def onchange_partner_id_member(self):
        self.ensure_one()
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email

    def compute_count_invoices(self):
        for rec in self:
            rec.sh_invoice_count = self.env['account.move'].sudo().search_count(
                [('sh_membership_id', '=', rec.id)])

    def sh_action_view_invoices(self):
        self.ensure_one()
        invoices = self.env['account.move'].sudo().search(
            [('sh_membership_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [
                (self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                        for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def invoice_generate(self):
        self.ensure_one()
        invoice_vals = {}
        invoice_id = False
        journal_id = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', 'sale')
        ], limit=1)
        invoice_vals.update({
            'sh_membership_id': self.id,
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'journal_id': journal_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'currency_id': self.currency_id.id,
                'price_unit': self.sh_member_amount,
                'sh_card_no': self.barcode,
                'name': 'Parking Invoice',
            })]
        })
        invoice_id = self.env['account.move'].sudo().create(
            invoice_vals)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type")
        if len(invoice_id) > 1:
            action['domain'] = [('id', 'in', invoice_id.ids)]
        elif len(invoice_id) == 1:
            form_view = [
                (self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                        for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoice_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def sh_action_view_history(self):
        self.ensure_one()
        history = self.env['sh.parking.history'].sudo().search(
            [('sh_membership_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sh_parking_mgmt.sh_parking_history_action")
        action['domain'] = [('id', 'in', history.ids)]
        action = {'type': 'ir.actions.act_window_close'}
        return action
