# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'print_statement_count' in counters:
            values['print_statement_count'] = 1
        return values

    @http.route([
        '/account_statement/print_statement/'],
        type='http',
        auth="user",
        website=True
    )
    def print_statements_custom(self, **post):
        partner_id = request.env.user.partner_id
#        pdf = request.env.ref(
#            'portal_account_customer_statement.website_partnerledgercustomer'
#        ).with_context(from_portal_report=True, company_id=request.website.company_id).sudo()._render_qweb_pdf([partner_id.id])[0]
        pdf = request.env['ir.actions.report'].with_context(from_portal_report=True, company_id=request.env.company).sudo()._render_qweb_pdf('portal_account_customer_statement.website_partnerledgercustomer', [partner_id.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route([
        '/my/print_statement_custom',
        '/my/print_statement_custom/page/<int:page>'
    ], type='http', auth="user", website=True)
    def portal_my_print_statements_custom(self, page=1, **kw):
        return request.render(
            "portal_account_customer_statement.my_customer_portal_statements_custom"
        )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
