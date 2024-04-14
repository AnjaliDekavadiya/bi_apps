# -*- coding: utf-8 -*-

import logging
import os
import datetime
import werkzeug
import json
from odoo import http
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from collections import OrderedDict
from odoo import _

_logger = logging.getLogger(__name__)


class DxSaasControllers(http.Controller):
    @http.route('/database/backup_now/<int:subscription_id>/<int:server_id>/<string:backup_format>', type='http',
                auth="user", methods=['GET'], csrf=False)
    def backup_database(self, server_id, subscription_id, backup_format, **kwargs):
        try:
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            is_admin = http.request.env.user.has_group('dx_saas_dbfilter.group_dx_saas_dbfilter_manager')
            if is_admin:
                subscription_data = http.request.env["dx.saas.dbfilter.subscriptions"].sudo().search(
                    [('id', '=', subscription_id)])
            else:
                subscription_data = http.request.env["dx.saas.dbfilter.subscriptions"].sudo().search(
                    [('id', '=', subscription_id), ("client_id", "=", http.request.env.user.partner_id.id)])
            server_data = http.request.env["dx.saas.dbfilter.servers"].sudo().search([('id', '=', server_id)])

            database_name = subscription_data.domain
            master_pasword = server_data.master_password
            url = server_data.url_protocol + server_data.url + ":" + str(
                server_data.public_http_port) + "/web/database/backup"
            filename = "%s_%s.%s" % (database_name, ts, backup_format)

            destination = "/tmp/" + str(filename)
            command = 'curl -X POST -F "master_pwd=%s" -F "name=%s" -F "backup_format=%s" -o "%s"' \
                      ' "%s"' % (master_pasword, database_name, backup_format, destination, url)
            os.system(command)
            headers = [
                ('Content-Type', 'application/octet-stream; charset=binary'),
                ('Content-Disposition', http.content_disposition(filename)),
            ]
            with open(destination, 'rb') as f:
                text = f.read()
            response = werkzeug.wrappers.Response(text, headers=headers, direct_passthrough=True)
            return response
        except Exception as e:
            _logger.exception('Database.backup %s' % e)
            return {"status": "Forbidden", "code": 403}


class DxControlUsersAndModules(http.Controller):

    @http.route('/dx_saas_check', type='json', auth="public", methods=['POST'], csrf=False)
    def check_users(self):
        try:
            data = json.loads(http.request.httprequest.data)
            subscription_data = http.request.env['dx.saas.dbfilter.subscriptions'].sudo().search(
                [('domain', '=', data["db"])])
            if data["tocheck"] == "users":
                users_count = subscription_data.users_count
                return {"status": "success", "code": 200, "data": users_count}
            elif data["tocheck"] == "modules":
                modules = ['dx_users_modules_control']
                for package in subscription_data.packages_id:
                    for module in package.modules_id:
                        modules.append(module.technical_name)
                modules = list(dict.fromkeys(modules))
                return {"status": "success", "code": 200, "data": modules}
        except:
            return {"status": "error", "code": 404}


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'subscriptions_count' in counters:
            values['subscriptions_count'] = http.request.env['dx.saas.dbfilter.subscriptions'].sudo().search_count(
                [("client_id", "=", http.request.env.user.partner_id.id)])
        return values

    @http.route(['/my/dx/saas/subscriptions', '/my/dx/saas/subscriptions/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_saas_subscriptions(self, page=1, sortby=None, filterby=None, start_date=None, end_date=None, **kw):
        SubscriptionsObject = http.request.env['dx.saas.dbfilter.subscriptions']

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'start_date': {'label': _('Start Date'), 'order': 'start_date asc'},
            'end_date': {'label': _('End Date'), 'order': 'end_date asc'},
            'state': {'label': _('State'), 'order': 'state asc'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {}
        subscriptions_count = SubscriptionsObject.sudo().search_count(
            [("client_id", "=", http.request.env.user.partner_id.id)])
        pager = portal_pager(
            url="/my/dx/saas/subscriptions",
            url_args={'date_begin': start_date, 'end_date': end_date},
            total=subscriptions_count,
            page=page,
            step=self._items_per_page
        )
        subscriptions = SubscriptionsObject.sudo().search(
            [("client_id", "=", http.request.env.user.partner_id.id)],
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        http.request.session['my_subscriptions_history'] = subscriptions.ids[:100]

        values = {
            'start_date': start_date,
            'subscriptions': subscriptions,
            'page_name': 'Subscriptions',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        }
        return http.request.render("dx_saas_dbfilter.dx_saas_dbfilter_portal_template", values)
