# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _get_total_progress_billing(self):
        for aml in self:
            aml.total_progress_billing = aml.analytic_id.total_progress_billing

    def _get_invoice_to_date(self):
        for aml in self:
            if aml.move_type in ['out_invoice','out_refund','out_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('move_type', 'in' ,['out_invoice','out_refund','out_receipt'])])
                if invoiced_ids:
                    inv_amount_total = 0
                    for inv in invoiced_ids:
                       inv_amount_total += inv.amount_total
                    aml.invoice_to_date = inv_amount_total
                else:
                    aml.invoice_to_date = 0
            elif aml.move_type in ['in_invoice','in_refund','in_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('move_type', 'in' ,['in_invoice','in_refund','in_receipt'])])
                if invoiced_ids:
                    inv_amount_total = 0
                    for inv in invoiced_ids:
                       inv_amount_total += inv.amount_total
                    aml.invoice_to_date = inv_amount_total
                else:
                    aml.invoice_to_date = 0
            else:
                aml.invoice_to_date = 0

    def _get_previous_invoiced(self):
        for aml in self:
            if aml.move_type in ['out_invoice','out_refund','out_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('move_type', 'in' ,['out_invoice','out_refund','out_receipt'])],order='id ASC',limit=1)
                if invoiced_ids:
                    for inv in invoiced_ids:
                        aml.previous_invoiced += inv.amount_total
                else:
                    aml.previous_invoiced = 0
            elif aml.move_type in ['in_invoice','in_refund','in_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('move_type', 'in' ,['in_invoice','in_refund','in_receipt'])],order='id ASC',limit=1)
                if invoiced_ids:
                    for inv in invoiced_ids:
                        aml.previous_invoiced += inv.amount_total
                else:
                    aml.previous_invoiced = 0
            else:
                aml.previous_invoiced = 0

    def _get_previous_invoice_due(self):
        for aml in self:
            if aml.move_type in ['out_invoice','out_refund','out_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('move_type', 'in' ,['out_invoice','out_refund','out_receipt'])],order='id ASC', limit=1)
                
                if invoiced_ids:
                  aml.previous_invoice_due = invoiced_ids.amount_residual
                else:
                    aml.previous_invoice_due = 0
            elif aml.move_type in ['in_invoice','in_refund','in_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('move_type', 'in' ,['in_invoice','in_refund','in_receipt'])],order='id ASC', limit=1)
                
                if invoiced_ids:
                  aml.previous_invoice_due = invoiced_ids.amount_residual
                else:
                    aml.previous_invoice_due = 0
            else:
                aml.previous_invoice_due = 0

    def _get_remaining_progress(self):
        total = 0
        for aml in self:
            total = aml.analytic_id.total_progress_billing - aml.invoice_to_date
            if total < 0:
                aml.remaining_progress = 0.0
            else:
                aml.remaining_progress = total

    def _get_current_invoice(self):
        for aml in self:
            aml.current_invoice = aml.amount_total
    

    def _get_total_due(self):
        for aml in self:
            
            if aml.move_type in ['out_invoice','out_refund','out_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('payment_state','not in',['in_payment','paid']),('move_type', 'in' ,['out_invoice','out_refund','out_receipt'])])
                if invoiced_ids:
                    total = 0
                    for inv in invoiced_ids:
                        if inv.id == aml.id  :
                            aml.total_due = aml.current_invoice
                        else:
                          total += inv.amount_total
                    aml.total_due = aml.current_invoice + total
                else:
                    aml.total_due = 0
            
            elif aml.move_type in ['in_invoice','in_refund','in_receipt']:
                invoiced_ids = self.search(
                    [('partner_id', '=', aml.partner_id.id), ('invoice_date', '<=', datetime.date.today()),
                     ('company_id', '=', aml.company_id.id),('analytic_id','=',aml.analytic_id.id),('payment_state','not in',['in_payment','paid']),('move_type', 'in' ,['in_invoice','in_refund','in_receipt'])])
                if invoiced_ids:
                    total = 0
                    for inv in invoiced_ids:
                        if inv.id == aml.id  :
                            aml.total_due = aml.current_invoice
                        else:
                          total += inv.amount_total
                    aml.total_due = aml.current_invoice + total
                else:
                    aml.total_due = 0
            else:
                aml.total_due = 0
            



    progress_billing_title = fields.Char(string="Progress Billing Title")
    analytic_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    total_progress_billing = fields.Float(compute='_get_total_progress_billing', string="Total Progress Billing")
    previous_invoiced = fields.Float(compute='_get_previous_invoiced',string="Previously Invoiced", default=0.00)
    invoice_to_date = fields.Float(compute='_get_invoice_to_date', string="Invoice to Date", default=0.00)
    remaining_progress = fields.Float(compute='_get_remaining_progress', string="Remaining Progress Billing")
    previous_invoice_due = fields.Float(compute='_get_previous_invoice_due', string="Previously invoiced Due")
    current_invoice = fields.Float(compute='_get_current_invoice', string="Currently Invoiced")
    total_due = fields.Float(compute='_get_total_due', string="Total Due Now")
