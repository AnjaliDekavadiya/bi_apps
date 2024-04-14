# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http, tools, SUPERUSER_ID, _
from odoo.http import request

_logger = logging.getLogger(__name__)

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class CustomerPortalSubcontract(CustomerPortal):
    
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortalSubcontract, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        SubcontractOrder = request.env['job.subcontract']
        
        subcontract_count = SubcontractOrder.search_count([
            ('assigned_to.partner_id', '=', partner.id)])
        
        values.update({
            'subcontract_count': subcontract_count,
        })
        return values
        
    
    @http.route(['/my/subcontractor-job-order', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_subcontractor_job_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SubcontractOrder = request.env['job.subcontract']

        domain = [
            ('assigned_to.partner_id', '=', partner.id)]

        # default sortby order
        #archive_groups = self._get_archive_groups('sale.order', domain)
        #if date_begin and date_end:
            #domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        subcontract_count = SubcontractOrder.search_count(domain)
        
        # make pager
        pager = portal_pager(
            url="/my/subcontractor-job-order",
            #url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=subcontract_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        subcontracts = SubcontractOrder.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_subcontract_history'] = subcontracts.ids[:100]

        values.update({
            #'date': date_begin,
            'subcontracts': subcontracts.sudo(),
            'page_name': 'subcontract',
            'pager': pager,
            #'archive_groups': archive_groups,
            'default_url': '/my/subcontractor-job-order',
            #'searchbar_sortings': searchbar_sortings,
            #'sortby': sortby,
        })
        return request.render("bi_odoo_job_subcontracting.portal_my_subcontractor_orders", values)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
