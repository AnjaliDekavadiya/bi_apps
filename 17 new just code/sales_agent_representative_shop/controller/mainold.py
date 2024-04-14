# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import api, http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        res = super(WebsiteSale, self)._get_shop_payment_values(order=order,kwargs=kwargs)
        sales_agent_ids = request.env['res.partner'].sudo().search([('is_web_sales_agent', '=', True)])
        web_shop_agent_level = request.env['sale.commission.level'].sudo().search([('web_shop_agent_level', '=', True)])
        website_sale_order = res.get('website_sale_order')
        sale_commission_user_ids = website_sale_order.sale_commission_user_ids.filtered(lambda comm_user: comm_user.level_id.web_shop_agent_level)
        res.update({
            'custom_sales_agent_ids': sales_agent_ids,
            'web_shop_agent_level': web_shop_agent_level,
            'custom_sale_commission_user_id': sale_commission_user_ids[0] if sale_commission_user_ids else False,
        })
        return res

    @http.route(['/sale/shop/addagent'], type="http", auth='public',method=['POST'], website=True)
    def sale_shop_addagent(self, **kwargs):
        sale_order = request.env['sale.order'].browse(int(kwargs.get('website_sale_order')))
        web_shop_agent_level = request.env['sale.commission.level'].sudo().search([('web_shop_agent_level', '=', True)])
        web_shop_sales_person_level = False
        partner = request.env.user.partner_id
        if partner.add_sales_person_to_so:
            web_shop_sales_person_level = request.env['sale.commission.level'].sudo().search([('web_shop_sales_person_level', '=', True)])
        
        comm_user_setting_vals_lst = []
        if web_shop_agent_level and kwargs.get('custom_sale_commission_user_id') and kwargs.get('custom_sales_agent_id'):
            comm_user_id = request.env['sale.commission.level.users'].sudo().browse(int(kwargs.get('custom_sale_commission_user_id')))
            comm_user_id.sudo().write({
                'user_id': int(kwargs.get('custom_sales_agent_id')),
            })
        elif web_shop_agent_level and kwargs.get('custom_sales_agent_id'):
            comm_user_setting_vals = {
                'level_id': web_shop_agent_level.id,
                'user_id': int(kwargs.get('custom_sales_agent_id')) if kwargs.get('custom_sales_agent_id') else False,
                'order_id': sale_order.id,
            }
            comm_user_setting_vals_lst.append((0, 0, comm_user_setting_vals))
            if web_shop_sales_person_level and partner.user_id:
                comm_user_setting_vals = {
                    'level_id': web_shop_sales_person_level.id,
                    'user_id': partner.user_id.partner_id.id,
                    'order_id': sale_order.id,
                }
                comm_user_setting_vals_lst.append((0, 0, comm_user_setting_vals))
        if comm_user_setting_vals_lst:
            sale_order.sudo().write({
                'sale_commission_user_ids': comm_user_setting_vals_lst,
                'custom_webshop_add_agent': True,
            })
            commission_based_on = request.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on')
            if commission_based_on in ['product_category', 'product_template']:
                for line in sale_order.order_line:
                    line.sudo().product_id_change()
            elif commission_based_on == 'sales_team':
                sale_order.sudo().team_id_change()
        return request.redirect(request.httprequest.referrer)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
