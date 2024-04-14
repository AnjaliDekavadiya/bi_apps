# Copyright (C) Softhealer Technologies.

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers import main


class SaleProductCallForPrice(http.Controller):

    @http.route(['/sale/product_call_for_price'], type='json', auth="public", methods=['POST'], website=True)
    def sale_product_call_for_price(self, **post):

        if post.get('product_id', False):

            product_search = request.env['product.product'].sudo().search(
                [('id', '=', post.get('product_id'))], limit=1)

            if product_search:

                vals = {'name': product_search.id}

                if post.get('first_name', False):
                    vals.update({'contact_name': post.get('first_name')})

                if post.get('email', False):
                    vals.update({'email_from': post.get('email')})

                if post.get('contact_no', False):
                    vals.update({'mobile': post.get('contact_no')})

                if post.get('message', False):
                    vals.update({'name': post.get('message')})

                vals.update({'type': 'lead'})

                call_price_obj = request.env['crm.lead'].sudo().create(
                    vals)

                if call_price_obj.user_id._is_public():
                    call_price_obj.user_id = False

                if call_price_obj:
                    quotation_create = request.env['sh.crm.lead.product.quote'].sudo().create(
                        {'lead_id': call_price_obj.id, 'quantity': post.get('quantity'), 'product_id': int(post.get('product_id', False))})
                    quotation_create.onchange_product_id()
                if call_price_obj:
                    return 1
        return 0


class Website(main.Website):

    @http.route()
    def autocomplete(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):
        res = super(Website, self).autocomplete(search_type=search_type, term=term, order=order,
                                                limit=limit, max_nb_chars=max_nb_chars, options=options)
        if res and res.get('results', False):
            final_result = []
            for product_dic in res.get('results'):
                if product_dic.get("call_for_price", False):
                    product_dic["detail"] = ''
                    product_dic["detail_strike"] = ''
                final_result.append(product_dic)

            res['results'] = final_result
        return res
