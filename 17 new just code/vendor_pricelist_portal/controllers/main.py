# -*- coding: utf-8 -*-

from odoo import http, modules, SUPERUSER_ID
from odoo import http , _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        domain = [
            # ('name', 'child_of', [partner.commercial_partner_id.id])
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        custom_product_pricelist_count = request.env['product.supplierinfo'].sudo().search_count(domain)
        values.update({
            'custom_product_pricelist_count': custom_product_pricelist_count,
        })
        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [
            # ('name', 'child_of', [partner.commercial_partner_id.id])
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        custom_product_pricelist_count = request.env['product.supplierinfo'].sudo().search_count(domain)
        values.update({
            'custom_product_pricelist_count': custom_product_pricelist_count,
            'page_name': 'pricelist_probc',
        })
        return values

    #open product.supplierinfo list view
    @http.route(['/custom/product/pricelist', '/custom/product/pricelist/page/<int:page>'], type='http', auth="user", website=True)
    def portal_custom_product_pricelists(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        domain = [
            # ('name', 'child_of', [partner.commercial_partner_id.id])
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        custom_product_pricelist_count = request.env['product.supplierinfo'].sudo().search_count(domain)

        searchbar_sortings = {
            'product_tmpl_id': {'label': _('Product Name'), 'order': 'product_tmpl_id'},
            'product_id': {'label': _('Product Variant'), 'order': 'product_id'},
            'product_name': {'label': _('Vendor Product Name'), 'order': 'product_name'},
            'product_code': {'label': _('Vendor Product Code'), 'order': 'product_code'},
            'date_start': {'label': _('Start Date Ascending'), 'order': 'date_start'},
            'date_end': {'label': _('End Date Ascending'), 'order': 'date_end'},
            'date_start desc': {'label': _('Start Date Descending'), 'order': 'date_start desc'},
            'date_end desc': {'label': _('End Date Descending'), 'order': 'date_end desc'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'product_tmpl_id': {'input': 'product_tmpl_id', 'label': _('Search by Product Name')},
            'product_id': {'input': 'product_id', 'label': _('Search by Product Variant')},
            'product_name': {'input': 'product_name', 'label': _('Search by Vendor Product Name')},
            'product_code': {'input': 'product_code', 'label': _('Search by Vendor Product Code')},
        }

        if not sortby:
            sortby = 'product_tmpl_id'
        order = searchbar_sortings[sortby]['order']

        if search and search_in:
            search_domain = []
            if search_in in ('product_tmpl_id', 'all'):
                search_domain = OR([search_domain, [('product_tmpl_id', 'ilike', search)]])
            if search_in in ('product_id', 'all'):
                search_domain = OR([search_domain, [('product_id', 'ilike', search)]])
            if search_in in ('product_name', 'all'):
                search_domain = OR([search_domain, [('product_name', 'ilike', search)]])
            if search_in in ('product_code', 'all'):
                search_domain = OR([search_domain, [('product_code', 'ilike', search)]])
            domain += search_domain


        pricelist = request.env['product.supplierinfo']
        pricelists = pricelist.sudo().search(domain)

        pager = portal_pager(
            url="/custom/product/pricelist",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=custom_product_pricelist_count,
            page=page,
            step=self._items_per_page
        )

        pricelists = pricelist.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'pricelists': pricelists,
            'page_name': 'pricelist_probc',
            'default_url': '/custom/product/pricelist',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'custom_product_pricelist_count': custom_product_pricelist_count,
            'sortby': sortby,
          
        })
        return request.render("vendor_pricelist_portal.custom_display_product_pricelist", values)

    #open product.supplierinfo form view
    @http.route(['/custom/product/pricelist/<int:pricelist_request_id>'], type='http', auth="user", website=True)
    def custom_portal_pricelist_requests(self, pricelist_request_id, **kw):
        pricelist = request.env['product.supplierinfo'].sudo().browse(pricelist_request_id)
        partner = request.env.user.partner_id
        # if pricelist.name.id not in partner.commercial_partner_id.ids:
        if pricelist.partner_id.id not in partner.commercial_partner_id.ids:
            return request.redirect('/my')
        values = {'pricelist_request': pricelist}
        return request.render("vendor_pricelist_portal.custom_display_pricelist_products", values)


class WebsiteProductPricelistComment(http.Controller):
        
    # @http.route(['/custom_pricelist/comment'], type='http', auth="user", website=True)
    # def custom_pricelist_comment(self, **kw):
    #     product_tmpl_object = request.env['product.template']
    #     custom_pricelist_comment = kw.get('custom_pricelist_comment')
    #     pricelist_id =  request.env['product.supplierinfo'].sudo().browse(int((kw.get('custom_pricelist_comment_id'))))
    #     product_tmplate_id = product_tmpl_object.browse(pricelist_id.product_tmpl_id.id)
    #     product_tmplate_id.sudo().message_post(body=custom_pricelist_comment)
    #     url = '/custom/product/pricelist/' + str(pricelist_id.id)
    #     return request.redirect(url)

    @http.route(['/custom_pricelist/comment'], type='json', auth="user", website=True)
    def custom_pricelist_comment(self, **kw):
        product_tmpl_object = request.env['product.template']
        custom_pricelist_comment = kw.get('comment')
        pricelist_id =  request.env['product.supplierinfo'].sudo().browse(int((kw.get('pricelist_id'))))
        product_tmplate_id = product_tmpl_object.browse(pricelist_id.product_tmpl_id.id)
        product_tmplate_id.sudo().message_post(body=custom_pricelist_comment)
        return True