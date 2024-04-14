# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import api, http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import _build_url_w_params


class SalesAgentRemove(http.Controller):

    @http.route(['/custom/sales_aget/remove'], type='http', auth="user", website=True)
    def custom_sales_aget_remove(self, **kwargs):
        sales_order_id = request.env['sale.order'].sudo().browse(int(kwargs.get('website_sale_order')))
        for comm_user_id in sales_order_id.sale_commission_user_ids:
            comm_user_id.unlink()
        sales_order_id.write({
            'custom_webshop_add_unique_agent': False,
        })
        return request.redirect(request.httprequest.referrer)


class WebsiteSale(WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        res = super(WebsiteSale, self)._get_shop_payment_values(order=order,kwargs=kwargs)
        # sales_agent_ids = request.env['res.partner'].sudo().search([('is_web_sales_agent', '=', True)])
        # web_shop_agent_level = request.env['sale.commission.level'].sudo().search([('web_shop_agent_level', '=', True)])
        website_sale_order = res.get('website_sale_order')
        sale_commission_user_ids = website_sale_order.sale_commission_user_ids.filtered(lambda comm_user: comm_user.level_id.web_shop_agent_level)
        res.update({
            'custom_sales_agent_ids': res['custom_sales_agent_ids'],
            'web_shop_agent_level': res['web_shop_agent_level'],
            'custom_sale_unique_user_id': sale_commission_user_ids[0] if sale_commission_user_ids else False,
            'sale_unique_users_partner': False,
            'sale_unique_users_partner_search': kwargs.get('sale_unique_users_partner_search'),
        })
        return res

    @http.route(['/sale/shop/search_agent_custom'], type="http", auth='public',method=['POST'], website=True)
    def sale_shop_search_agent_custom(self, **kwargs):
        sale_order = request.env['sale.order'].sudo().browse(int(kwargs.get('website_sale_order')))
        web_shop_agent_level = request.env['sale.commission.level'].sudo().browse(int(kwargs.get('custom_web_shop_agent_level')))#request.env['sale.commission.level'].sudo().search([('web_shop_agent_level', '=', True)])
        web_shop_sales_person_level = False
        partner = request.env.user.partner_id
        if partner.add_sales_person_to_so:
            web_shop_sales_person_level = request.env['sale.commission.level'].sudo().search([('web_shop_sales_person_level', '=', True)])
        comm_user_setting_vals_lst = []
        sale_unique_users_partner_id = False
        if kwargs.get('custom_sale_unique_users_input'):
            sale_unique_users_partner_id = request.env['res.users'].sudo().search([('custom_number', '=', kwargs.get('custom_sale_unique_users_input'))]).filtered(lambda user:user.is_web_sales_agent == True)

        if sale_unique_users_partner_id:
            if web_shop_agent_level and kwargs.get('custom_sale_unique_user_id') and kwargs.get('custom_sale_unique_users_input'):
    #            unique_user_id = request.env['res.users'].search([('custom_number', '=', kwargs.get('custom_sale_unique_users_input'))])
                comm_user_id = request.env['sale.commission.level.users'].sudo().browse(int(kwargs.get('custom_sale_unique_user_id')))
                comm_user_id.sudo().write({
                    'user_id': sale_unique_users_partner_id.partner_id.id,#int(kwargs.get('custom_sale_unique_users_input')),
                })
            elif web_shop_agent_level and kwargs.get('custom_sale_unique_users_input'):
                comm_user_setting_vals = {
                    'level_id': web_shop_agent_level.id,
                    'user_id': sale_unique_users_partner_id.partner_id.id,#int(kwargs.get('custom_sale_unique_users_input')) if kwargs.get('custom_sale_unique_users_input') else False,
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
                    'custom_webshop_add_unique_agent': True,
                })
                commission_based_on = request.env['ir.config_parameter'].sudo().get_param('sales_commission_external_user.commission_based_on')
                if commission_based_on in ['product_category', 'product_template']:
                    for line in sale_order.order_line:
                        sale_commission_percentage = []
                        if commission_based_on == 'product_category':
                            for level in line.product_id.categ_id.sale_commission_percentage_ids:
                                sale_commission_percentage.append(level.id)
                        elif commission_based_on == 'product_template':
                            for level in line.product_id.sale_commission_percentage_ids:
                                sale_commission_percentage.append(level.id)
                        line.commission_percentage_ids = [(6, 0, sale_commission_percentage)]
                elif commission_based_on == 'sales_team':
                    sale_commission_percentage = [(5, 0)]
                    for level in sale_order.sudo().team_id.sale_commission_percentage_ids:
                        sale_commission_percentage.append((0,0,{'level_id': level.level_id.id,
                                                'percentage': level.percentage,
                                                'sale_order_id':sale_order.id}))
                    sale_order.sale_commission_percentage_ids = sale_commission_percentage
        partner_msg_dict = {}
        if sale_unique_users_partner_id:
            partner_msg_dict.update({
                'sale_unique_users_partner_search': '',
            })
        else:
            partner_msg_dict.update({
                'sale_unique_users_partner_search': kwargs.get('custom_sale_unique_users_input'),
            })

        return request.redirect(_build_url_w_params(request.httprequest.referrer, partner_msg_dict), code=301)
#        return request.redirect(request.httprequest.referrer)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
