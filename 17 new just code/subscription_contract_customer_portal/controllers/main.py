# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo import models,registry, SUPERUSER_ID
# from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.portal.controllers.portal import CustomerPortal as website_account , pager as portal_pager, get_records_pager

class website_account(website_account):

    def _prepare_portal_layout_values(self): # odoo11
        values = super(website_account, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'custom_contract_count': request.env['account.analytic.account'].sudo().search_count([('partner_id', 'child_of', [partner.commercial_partner_id.id])]),
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        values['custom_contract_count'] = request.env['account.analytic.account'].sudo().search_count([
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ])
        return values

#     @http.route()
#     def account(self, **kw):
#         """ Add contract documents to main account page """
#         response = super(website_account, self).account(**kw)
#         partner = request.env.user.partner_id
#         contract = request.env['account.analytic.account']
#         custom_contract_count = contract.sudo().search_count([
#         ('partner_id', 'child_of', [partner.commercial_partner_id.id])
#           ])
#         response.qcontext.update({
#         'custom_contract_count': custom_contract_count,
#         })
#         return response
        
    @http.route(['/my/custom/contracts', '/my/custom/contracts/page/<int:page>'], type='http', auth="user", website=True)
    def custom_portal_my_contract(self, page=1, **kw):
        response = super(website_account, self)
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        contract_obj = http.request.env['account.analytic.account']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        custom_contract_count = contract_obj.sudo().search_count(domain)
        # pager
        # pager = request.website.pager(
        #     url="/my/custom/contracts",
        #     total=custom_contract_count,
        #     page=page,
        #     step=self._items_per_page
        # )

        pager = portal_pager(
            url="/my/custom/contracts",
            total=custom_contract_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        contracts = contract_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'contracts': contracts,
            'page_name': 'contract',
            'pager': pager,
            'default_url': '/my/custom/contracts',
        })
        return request.render("subscription_contract_customer_portal.custom_display_contracts", values)
        
    @http.route(['/my/custom/contact_print/<int:contract>'], type='http', auth="user", website=True)
    def contract_print(self, contract=None, **kw):
#         pdf = request.env['report'].sudo().get_pdf([contract], 'contract_recurring_invoice_analytic.contract_report_view', data=None)
#         pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
#         return request.make_response(pdf, headers=pdfhttpheaders)
        contract_obj = http.request.env['account.analytic.account']
        contract_id = contract_obj.sudo().browse(int(contract))
        partner = request.env.user.partner_id #04/01/2020

        if contract_id.partner_id.commercial_partner_id.id != partner.commercial_partner_id.id:
            return request.redirect('/my')
        
        report_action = 'contract_recurring_invoice_analytic.contract_recurring_invoice_analytic_report'
        # pdf = request.env.ref(report_action).sudo().render_qweb_pdf([contract])[0]
        # pdf = request.env.ref(report_action).sudo()._render_qweb_pdf([contract])[0]
        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('contract_recurring_invoice_analytic.contract_recurring_invoice_analytic_report',[contract])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    def _prepare_custom_contract_portal(self, contract, kw):
        contract_obj = http.request.env['account.analytic.account']
        contract_id = contract_obj.sudo().browse(int(contract))
        values={
            'contract_id': contract_id,
        }
        return values

    @http.route(['/my/custom/contract/<int:contract>'], type='http', auth="user", website=True)
    def portal_contract(self, contract=None, access_token=None, **kw):
        contract_obj = http.request.env['account.analytic.account']
        contract_id = contract_obj.sudo().browse(int(contract))
        partner = request.env.user.partner_id #04/01/2020

        if contract_id.partner_id.commercial_partner_id.id != partner.commercial_partner_id.id:
            return request.redirect('/my')
        values = self._prepare_custom_contract_portal(contract, kw)
        # partner = request.env.user.partner_id

        values.update({
            'page_name': 'page_portal_contract',
            'partner': partner,
        })
        return request.render("subscription_contract_customer_portal.custom_display_contract", values)
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
