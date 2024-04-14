# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request


class WebsitePrintCustomerInvoice(http.Controller):
    
    @http.route(['/ci_invoice/print'], type='http', auth="public", website=True)
    def custom_print_customer_invoice(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        for invoice_id in order.invoice_ids:
            if order:
#                pdf, _ = request.env.ref('account.account_invoices').sudo()._render_qweb_pdf([invoice_id.id])
#                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
#                return request.make_response(pdf, headers=pdfhttpheaders)
                pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('account.account_invoices', [invoice_id.id])
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
                return request.make_response(pdf, headers=pdfhttpheaders)
            else:
                return request.redirect('/shop')
       
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
