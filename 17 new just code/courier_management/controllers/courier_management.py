# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Albin P J(odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal


class CourierRequests(http.Controller):
    """This controller is for portal"""

    def _get_courier_domain(self):
        """It returns the login person"""
        return [('sender_id', '=', request.env.user.partner_id.id)]

    @http.route(['/my/courier/requests'], type='http', auth="user",
                website=True)
    def get_my_courier_requests(self):
        """Take values from courier requests and render to portal tree
        template """
        domain = self._get_courier_domain()
        values = {
            'courier_request': request.env['courier.request'].sudo().search(
                domain),
        }
        return request.render(
            "courier_management.portal_my_courier_requests_tree", values)

    @http.route(['/my/courier/requests/form/<int:courier_id>'], type='http',
                auth="user", website=True)
    def get_my_courier_request_form(self, courier_id):
        """Take values from courier_request and render to portal form
        template.It also passes the id in the root for rendering the
        corresponding form template"""
        return request.render(
            "courier_management.portal_my_courier_requests_form",
            {'record_courier_requests': request.env[
                'courier.request'].sudo().browse(courier_id)})

    @http.route(['/courier/requests/group/by'], type='json', auth="public",
                website=True)
    def courier_requests_group_by(self, **kwargs):
        """Call from rpc for group by, and it returns the corresponding
        values"""
        context = []
        group_value = kwargs.get("search_value")
        if group_value == '1':
            context = []
            for types in request.env['courier.type'].sudo().search([]):
                courier_requests_ids = request.env[
                    'courier.request'].sudo().search([
                     ('type_id', '=', types.id),
                     ('sender_id', '=', request.env.user.partner_id.id)
                    ])
                if courier_requests_ids:
                    context.append({
                        'name': types.courier_type,
                        'data': courier_requests_ids
                    })
        if group_value == '2':
            context = []
            for categories in request.env['courier.category'].sudo().search([]):
                courier_requests_ids = request.env[
                    'courier.request'].sudo().search([
                     ('category_id', '=', categories.id),
                     ('sender_id', '=', request.env.user.partner_id.id)
                    ])
                if courier_requests_ids:
                    context.append({
                        'name': categories.courier_category,
                        'data': courier_requests_ids
                    })
        values = {
            'courier_request': context,
        }
        response = http.Response(
            template='courier_management'
                     '.courier_requests_group_by_template',
            qcontext=values)
        return response.render()

    @http.route(['/courier/requests/search'], type='json', auth="public",
                website=True)
    def courier_requests_search(self, **kwargs):
        """It gives the values and return the response to corresponding
        template"""
        record = request.env["courier.request"].sudo().search(
            [('name', '=', kwargs.get("search_value")),
             ('sender_id', '=', request.env.user.partner_id.id)])
        response = http.Response(
            template='courier_management.portal_my_certificates_search',
            qcontext={'courier_request': record})
        return response.render()


class Return(portal.CustomerPortal):
    """This will take the count of total courier requests"""

    def _prepare_home_portal_values(self, counters):
        """This will return the certificates count"""
        values = super(Return, self)._prepare_home_portal_values(counters)
        values.update({
            'courier_requests_count': request.env[
                'courier.request'].sudo().search_count(
                [('sender_id', '=', request.env.user.partner_id.id)])
        })
        return values
