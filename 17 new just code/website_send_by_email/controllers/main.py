# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
# from odoo.addons.website_form.controllers.main import WebsiteForm #No need this line
from odoo.addons.website_sale.controllers.main import WebsiteSale
# from odoo.addons.website_sale.controllers.main import ProductConfiguratorController
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController #odoo13
from odoo import exceptions, _


# class WebsiteSale(ProductConfiguratorController):
class WebsiteSaleProductConfiguratorController(ProductConfiguratorController): #odoo13

    # @http.route(['/link'], type='json', auth="user", website=True)
    @http.route(['/send_email_probc'], type='json', auth="user", methods=['POST'], website=True) #odoo13
    def data_processing(self, output_data , data):
        user_id = request.env.user.partner_id.email
#        ctx = request._context.copy()
        ctx = request.env.context.copy()
        ctx.update({
                    'email_to':output_data
                    })
        sale_order_id = request.env['sale.order'].browse(int(data))
        template = request.env.ref('website_send_by_email.email_template_edi_customer_overdue_set1_probc')
        template.with_context(ctx).sudo().send_mail(sale_order_id.id)
        return True
