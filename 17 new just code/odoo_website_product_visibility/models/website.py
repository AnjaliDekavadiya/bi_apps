# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def _get_website_product_categores_visibility_data(self, search, results, categores):
        get_search_category_result = request.env['product.public.category']
        for data in results:
            if data.get('model') == 'product.public.category':
                get_search_category_result = data.get('results')
        if categores:
            category_result = list(set(categores.ids).intersection(get_search_category_result.ids))
            return request.env['product.public.category'].browse(category_result)
        else:
            return get_search_category_result

    def _get_website_product_visibility_data(self, search, results, categores, pro_templates, options, domain=[]):
        return_domain = False
        if categores and options.get('category'):
            domain += [('public_categ_ids', 'in', [options.get('category')])]
            return_domain = True
        if pro_templates and not options.get('category') and not search:
            domain += [
                ('id', 'in', pro_templates.ids)
            ]
            return_domain = True
        if search:
            get_search_product_result = request.env['product.template']
            for data in results:
                if data.get('model') == 'product.template':
                    get_search_product_result = data.get('results')

            if pro_templates:
                common_template_ids = list(set(pro_templates.ids).intersection(get_search_product_result.ids))
            else:
                common_template_ids = get_search_product_result.ids
            domain += [('id', 'in', common_template_ids)]
            return_domain = True
        if options.get('min_price') or options.get('max_price'):
            domain += [
                ('list_price', '>=', options.get('min_price') or 0.0),
                ('list_price', '<=', options.get('max_price') or 0.0)
            ]
            return_domain = True
        if options.get('attrib_values'):
            attrib_values = options.get('attrib_values')
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]
                return_domain = True
        if return_domain:
            return domain
        else:
            return []


    def _search_with_fuzzy(self, search_type, search, limit, order, options):
        ctx = self.env.context.copy()
        count, results, fuzzy_term = super(Website, self.with_context(ctx))._search_with_fuzzy(search_type, search, limit, order, options)

        domain = []
        public_user = request.env.user.has_group('base.group_public')
        base_domain = request.website.sale_product_domain()
        category_ids = request.env['product.public.category']
        template_ids = request.env['product.template']
        get_search_category_result = request.env['product.public.category']
        if not public_user:
            category_ids = request.env.user.partner_id.custom_visibility_category_ids
            template_ids = request.env.user.partner_id.custom_prob_template_ids
        else:
            shop_visibility_id = request.env['public.shop.visibility'].sudo().search([],limit=1)
            if shop_visibility_id:
                if not shop_visibility_id.all_category and shop_visibility_id.category_ids:
                    category_ids = shop_visibility_id.category_ids

                if not shop_visibility_id.all_product and shop_visibility_id.template_ids:
                    template_ids = shop_visibility_id.template_ids

        if not template_ids and not category_ids:
            return count, results, fuzzy_term

        domain = self._get_website_product_visibility_data(search, results, category_ids, template_ids, options, base_domain)
        if search:
            get_search_category_result = self._get_website_product_categores_visibility_data(search, results, category_ids)

        if domain:
            template_ids = request.env['product.template'].search(domain,order=order)
            for data in results:
                if data.get('model') == 'product.template':
                    data.update({
                        'results': template_ids,
                        'count': len(template_ids.ids or [])
                    })
                    count = len(template_ids.ids or [])

        if get_search_category_result:
            for data in results:
                if data.get('model') == 'product.public.category':
                    data.update({
                        'results': get_search_category_result,
                        'count': len(get_search_category_result.ids or [])
                    })
                    count = len(get_search_category_result.ids or [])

        return count, results, fuzzy_term