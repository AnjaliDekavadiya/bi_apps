# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################
from odoo import models, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vat_label = fields.Char(related='company_id.vat_label')
    vat_label_full = fields.Char(string='Vat label full', compute="_compute_vat_label")
    # Temporal field
    confirmation_date = fields.Datetime(string='Confirmation Date')

    def _compute_vat_label(self):
        for order in self:
            order.vat_label_full = '%s: %s' % ((order.company_id.account_fiscal_country_id.vat_label or 'Tax ID'), order.partner_id.vat) if order.partner_id.vat else ''
    
    def context_lang(self):
        return self.partner_id.lang

    def preview_report_invoice(self):
        if self:
            base_url = self[0].get_base_url()
        else:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        reportname = 'ReporSaleOrderPreview'
        report = self.env['ir.actions.report']._get_report_from_name(reportname)

        if not report:
            raise UserError(_("Has not defined any report with the template name of 'ReporSaleOrderPreview'"))

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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    image_medium = fields.Binary(related='product_id.image_128')
    full_tax_description = fields.Char(string='Full tax description', compute="_compute_full_tax_description")

    def _compute_full_tax_description(self):
        # Field compute tax description
        for line in self:
            line.full_tax_description = ', '.join([tax.description or tax.name for tax in line.tax_id])
