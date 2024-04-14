# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import models, fields, _, api
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # The related fields are just to keep the report formats intact
    # keeping fields from the previous version and not having to modify
    # template by template when migrating to a new version
    number_label = fields.Char(string='Number label report', compute='_compute_number_label')
    number = fields.Char(related='name')
    date_invoice = fields.Date(related='invoice_date')
    user_id = fields.Many2one(related='invoice_user_id')
    payment_term_id = fields.Many2one(related='invoice_payment_term_id')
    date_due = fields.Date(related='invoice_date_due')
    comment = fields.Html(related='narration')
    origin = fields.Char(related='invoice_origin')
    reference = fields.Char(related='ref')
    residual = fields.Monetary(related='amount_residual')
    invoice_payment_ref = fields.Char(related='payment_reference')
    total_qty = fields.Float(
        string='Total Quantity', digits='Product Unit of Measure', compute='_compute_total_qty')
    total_to_text = fields.Char(string='Total text', compute='_compute_total_to_text')
    total_to_text_upper = fields.Char(string='Total text upper', compute='_compute_total_to_text')

    @api.depends("amount_total")
    def _compute_total_to_text(self):
        for inv in self:
            inv.total_to_text = inv.currency_id.amount_to_text(inv.amount_total)
            inv.total_to_text_upper = inv.currency_id.amount_to_text(inv.amount_total).upper()

    def _compute_total_qty(self):
        for invoice in self:
            invoice.total_qty = sum([line.quantity for line in invoice.invoice_line_ids])

    def _compute_number_label(self):
        for invoice in self:
            if invoice.move_type == 'out_invoice' and invoice.state == 'posted':
                invoice.number_label = _('Invoice')
            elif invoice.move_type == 'out_invoice' and invoice.state == 'draft':
                invoice.number_label = _('Draft Invoice')
            elif invoice.move_type == 'out_invoice' and invoice.state == 'cancel':
                invoice.number_label = _('Cancelled Invoice')
            elif invoice.move_type == 'out_refund':
                invoice.number_label = _('Credit Note')
            elif invoice.move_type == 'in_refund':
                invoice.number_label = _('Vendor Credit Note')
            elif invoice.move_type == 'in_invoice':
                invoice.number_label = _('Vendor Bill')
            else:
                invoice.number_label = _('Invoice')

    def context_lang(self):
        return self.partner_id.lang

    def preview_report_invoice(self):
        if self:
            base_url = self[0].get_base_url()
        else:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        reportname = 'ReportAccountMovePreview'
        report = self.env['ir.actions.report']._get_report_from_name(reportname)

        if not report:
            raise UserError(_("Has not defined any report with the template name of 'ReportAccountMovePreview'"))

        if report.report_type == 'qweb-html':
            converter = 'html'
        elif report.report_type == 'qweb-pdf':
            converter = 'pdf'
        else:
            converter = 'text'
        ids = ','.join(map(str, self.ids))

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': f'{base_url}/report/{converter}/{report.report_name}/{ids}',
        }

    # Extend custom report use this method custom_report
    # & return a dictionary values
    def custom_report(self):
        payments = self.sudo().invoice_payments_widget and self.sudo().invoice_payments_widget['content'] or []
        tax_totals = self.tax_totals
        subtotals = []

        # Get taxes version 14.0
        tax_amount_by_group_14 = []
        
        for subtotal in tax_totals['subtotals']:
            subtotal_to_show = subtotal['name']
            values = {
                'name': subtotal_to_show,
                'amount': subtotal['amount'],
                'format_amount': subtotal['formatted_amount'],
            }
            tax_amount_by_group = []
            for amount_by_group in tax_totals['groups_by_subtotal'][subtotal_to_show]:
                if tax_totals['display_tax_base']:
                    tax_amount_by_group.append({
                        'tax_name': amount_by_group['tax_group_name'],
                        'amount': '%s %s' % (_('on '), amount_by_group['formatted_tax_group_base_amount']),
                        'tax': amount_by_group['formatted_tax_group_amount']
                    })
                    # Only for report
                    tax_amount_by_group_14.append({
                        'tax_name': amount_by_group['tax_group_name'],
                        'amount': '%s %s' % (_('on '), amount_by_group['formatted_tax_group_base_amount']),
                        'tax': amount_by_group['formatted_tax_group_amount']
                    })
                else:
                    tax_amount_by_group.append({
                        'tax_name': amount_by_group['tax_group_name'],
                        'amount': '',
                        'tax': amount_by_group['formatted_tax_group_amount']
                    })
                    # Only for report
                    tax_amount_by_group_14.append({
                        'tax_name': amount_by_group['tax_group_name'],
                        'amount': '',
                        'tax': amount_by_group['formatted_tax_group_amount']
                    })
            values.update({'amount_by_group': tax_amount_by_group})
            subtotals.append(values)

        for payment in payments:
            payment.update({
                'name': payment.get('name'),
                'paid_format_date': '%s %s' % (_('Paid on '), format_date(self.env, payment.get('date'))),
                'format_date': format_date(self.env, payment.get('date')),
                'format_amount': formatLang(self.env, payment.get('amount'), currency_obj=self.currency_id),
            })
        values = {
            "payments": payments,
            "subtotals": subtotals,
            "tax_totals": tax_totals,
            "tax_amount_by_group": tax_amount_by_group_14,
        }
        return values


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_line_tax_ids = fields.Many2many(related='tax_ids')
    uom_id = fields.Many2one(related='product_uom_id')
    full_tax_description = fields.Char(string='Full tax description', compute="_compute_full_tax_description")

    def _compute_full_tax_description(self):
        # Field compute tax description
        for line in self:
            line.full_tax_description = ', '.join([tax.description or tax.name for tax in line.tax_ids])
