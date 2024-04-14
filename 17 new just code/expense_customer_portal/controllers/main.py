# -*- coding: utf-8 -*-
from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import AND
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError


class PortalExpense(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalExpense, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        custom_expense_count = request.env['hr.expense'].sudo().search_count([('custom_partner_id', 'child_of', [partner.commercial_partner_id.id])])

        values['custom_expense_count'] = custom_expense_count
        return values


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        values['custom_expense_count'] = request.env['hr.expense'].sudo().search_count([('custom_partner_id', 'child_of', [partner.commercial_partner_id.id])])
        return values

    def _expense_get_page_view_values(self, expense, access_token, **kwargs):
        values = {
            'page_name': 'expense',
            'custom_expense': expense,
        }
        return self._get_page_view_values(expense, access_token, values, 'my_expense_history', False, **kwargs)

    @http.route(['/my/expense_custom', '/my/expense_custom/page/<int:page>'], type='http', auth="public", website=True)
    def custom_portal_my_expenses(self, page=1, date_begin=None, date_end=None, filterby=None, sortby=None, **kw):

        values = self._prepare_portal_layout_values()
        HrExpense = request.env['hr.expense']
        partner = request.env.user.partner_id

        domain = [('custom_partner_id', 'child_of', [partner.commercial_partner_id.id])]

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
        }
        
        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")), ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')), ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')), ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")), ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date', '>=', date_utils.start_of(last_month, 'month')), ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')), ('date', '<=', date_utils.end_of(last_year, 'year'))]},
        }

        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        custom_expense_count = HrExpense.sudo().search_count([])
        # pager
        pager = portal_pager(
            url="/my/expense_custom",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=custom_expense_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        expense = HrExpense.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_expense_history'] = expense.ids[:100]

        values.update({
            'date': date_begin,
            'expense': expense,
            'page_name': 'custom_expense_order_page',
            'pager': pager,
            'default_url': '/my/expense_custom',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("expense_customer_portal.portal_my_expense_custom", values)


    # @http.route(['/my/expense_custom/<int:expense_id>'], type='http', auth="user", website=True)
    # def custom_portal_my_expense(self, expense_id=None, access_token=None, **kw):
        # try:
        #     expense_sudo = self._document_check_access('hr.expense', expense_id, access_token=access_token)
        # except (AccessError, MissingError):
        #     return request.redirect('/my')

        # values = self._expense_get_page_view_values(expense_sudo, access_token, **kw)
        # return request.render("expense_customer_portal.custom_portal_my_expense", values)
        

    @http.route(['/my/expense_custom/<int:expense_id>'], type='http', auth="public", website=True)
    def custom_portal_my_expense(self, expense_id=None, access_token=None, **kw):
        partner = request.env.user.partner_id
        expense_id = request.env['hr.expense'].sudo().browse(expense_id)
        if partner.commercial_partner_id.id != expense_id.custom_partner_id.commercial_partner_id.id:
             return request.redirect("/")
        values = {'custom_expense': expense_id}
        return request.render("expense_customer_portal.custom_portal_my_expense", values)