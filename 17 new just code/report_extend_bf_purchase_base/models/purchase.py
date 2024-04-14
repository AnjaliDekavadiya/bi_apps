# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import models, fields, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    number_label = fields.Char(string='Number label report', compute='_compute_number_label')
    vat_label = fields.Char(related='company_id.vat_label')
    vat_label_full = fields.Char(string='Vat label full', compute="_compute_vat_label")

    def _compute_vat_label(self):
        for order in self:
            order.vat_label_full = '%s: %s' % ((order.company_id.account_fiscal_country_id.vat_label or 'Tax ID'), order.partner_id.vat) if order.partner_id.vat else ''

    def _compute_number_label(self):
        for record in self:
            if record.state == 'draft':
                record.number_label = _('Request for Quotation')
            elif record.state in ['sent', 'to approve']:
                record.number_label = _('Purchase Order')
            elif record.state in ['purchase', 'done']:
                record.number_label = _('Purchase Order Confirmation')
            elif record.state == 'cancel':
                record.number_label = _('Cancelled Purchase Order')
            else:
                record.number_label = _('Request for Quotation')
    
    def context_lang(self):
        return self.partner_id.lang

    def preview_report_invoice(self):
        if self:
            base_url = self[0].get_base_url()
        else:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        reportname = 'ReporPurchaseOrderPreview'
        report = self.env['ir.actions.report']._get_report_from_name(reportname)

        if not report:
            raise UserError(_("Has not defined any report with the template name of 'ReporPurchaseOrderPreview'"))

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


class PurchaseLine(models.Model):
    _inherit = "purchase.order.line"

    full_tax_description = fields.Char(string='Full tax description', compute="_compute_full_tax_description")

    def _compute_full_tax_description(self):
        # Field compute tax description
        for line in self:
            line.full_tax_description = ', '.join([tax.description or tax.name for tax in line.taxes_id])
