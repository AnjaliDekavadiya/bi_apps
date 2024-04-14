# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from operator import itemgetter
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
from odoo.addons.portal.controllers.portal import \
    CustomerPortal, pager as portal_pager


class WebsiteAccount(CustomerPortal):
    """Inherit CustomerPortal class"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # if 'certificate_count' in counters:
        if 'mail_message_count' in counters:
            partner_id = request.env.user.partner_id
            mail_message_obj = request.env['mail.message']
            mail_message_count = mail_message_obj.sudo().search_count([
                '|',
                ('partner_ids', 'in', partner_id.id),
                ('follower_partner_ids', 'in', partner_id.id),
                '|',
                ('subject', '!=', ''),
                ('body', '!=', '')
            ])
            values['mail_message_count'] = mail_message_count
        return values

    def _prepare_portal_layout_values(self):
        """Update a mail_message_count counter"""
        values = super(WebsiteAccount, self)._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id
        mail_message_obj = request.env['mail.message']
        mail_message_count = mail_message_obj.sudo().search_count([
            '|',
            ('partner_ids', 'in', partner_id.id),
            ('follower_partner_ids', 'in', partner_id.id),
            '|',
            ('subject', '!=', ''),
            ('body', '!=', '')
        ])
        values.update({
            'mail_message_count': mail_message_count,
        })
        return values

    def _mail_messages_get_page_view_values(self, message, access_token,
                                            **kwargs):
        """Get a page view"""
        values = {
            'page_name': 'message',
            'message': message.sudo(),
        }
        return self._get_page_view_values(message, access_token, values,
                                          'my_messages_history', False,
                                          **kwargs)

    @http.route(['/my/mail_messages', '/my/mail_messages/page/<int:page>'],
                type='http', auth="user", website=True)
    # def portal_my_mail_messages(self, page=1, sortby=None, filterby=None,
    #                             search=None, search_in='subject',
    #                             groupby='none', **kw):
    def portal_my_mail_messages(self, page=1, sortby=None, filterby=None,
                                search=None, search_in='all',
                                groupby='none', **kw):
        """Mail Message data get"""
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id
        domain = [
            '|',
            ('partner_ids', 'in', partner_id.id),
            ('follower_partner_ids', 'in', partner_id.id),
            '|',
            ('subject', '!=', ''),
            ('body', '!=', '')
        ]
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'subject'},
            'old_date': {'label': _('Oldest'), 'order': 'create_date asc'}
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': domain},
            'has_attachments': {
                'label': _('Has Attachments'),
                'domain': [('attachment_ids', '!=', False)]
            },
        }
        searchbar_inputs = {
            'content': {
                'input': 'content', 'label':
                _('Search <span class="nolabel"> (in Content)</span>')
            },
            'author': {'input': 'author', 'label': _('Search in Author')},
            'object': {'input': 'object', 'label': _('Search Model')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'model': {'input': 'model', 'label': _('Model')}
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # content according to pager and archive selected
        if groupby == 'model':
            order = "model, %s" % order
#         if groupby == 'author':
#             order = "author_id, %s" % order

        # default filter by value
        if not filterby:
            filterby = 'all'
        if filterby == 'all':
            domain = searchbar_filters[filterby]['domain']
        else:
            domain += searchbar_filters[filterby]['domain']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('object', 'all'):
                search_domain = OR([
                    search_domain,
                    [('model', 'ilike', search)]
                ])
            if search_in in ('author', 'all'):
                search_domain = OR([
                    search_domain,
                    [('author_id.name', 'ilike', search)]
                ])
            if search_in in ('content', 'all'):
                search_domain = OR([
                    search_domain,
                    [('body', 'ilike', search)]
                ])
            domain += search_domain

        # mail_messages count
        message_obj = request.env['mail.message'].sudo()
        mail_message_count = message_obj.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/mail_messages",
            url_args={
                'sortby': sortby,
                'filterby': filterby,
                'search_in': search_in,
                'search': search
            },
            total=mail_message_count,
            page=page,
            step=self._items_per_page
        )

        mail_messages = message_obj.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=(page - 1) * self._items_per_page
        )

        if groupby == 'model':
            grouped_messages = [request.env['mail.message'].concat(*g)
                                for k, g in
                                groupbyelem(
                                    mail_messages,
                                    itemgetter('model')
                                )]
        elif groupby == 'author':
            grouped_messages = [request.env['mail.message'].concat(*g)
                                for k, g in groupbyelem(
                                    mail_messages,
                                    itemgetter('author_id')
                                )]
        else:
            grouped_messages = [mail_messages]

        values.update({
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'grouped_messages': grouped_messages,
            'search_in': search_in,
            'groupby': groupby,
            'filterby': filterby,
            'sortby': sortby,
            'mail_messages': mail_messages,
            'page_name': 'mail_messages',
            'default_url': '/my/mail_messages',
            'pager': pager,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items()))
        })
        return request.render(
            "customer_supplier_message_portal.portal_mail_messages", values)

    @http.route(['/my/mail_message/<int:message>'], type='http',
                auth="public", website=True)
    def portal_my_mail_message(self, message=None, access_token=None, **kw):
        """Mail Message form data"""
        try:
            message_sudo = self._document_check_access(
                'mail.message',
                message, access_token
            )
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._mail_messages_get_page_view_values(
            message_sudo,
            access_token,
            **kw
        )
        return request.render(
            "customer_supplier_message_portal.portal_my_message", values)
