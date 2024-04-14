from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomCustomerPortal(WebsiteSale):

    @http.route('/my/custom_portal', type='http', auth='user', website=True)
    def custom_portal(self, **kw):
        orders = http.request.env['pragtech_tailoring_management.sale.order'].sudo().search([
            ('partner_id', '=', http.request.env.user.partner_id.id)
        ])
        return http.request.render('pragtech_tailoring_management.sale.portal_my_orders', {
            'orders': orders,
        })
    

class CustomerPortal(CustomerPortal):

    def _prepare_orders_domain(self, partner):
        super(CustomerPortal, self)._prepare_orders_domain(partner)
        domain = [
        ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
        ('state', '!=', 'draft'),
        ]
        return domain    