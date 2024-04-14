# -*- coding: utf-8 -*-

from operator import itemgetter
from odoo import http, _
from odoo.http import request
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        survey_user_input_count = request.env['survey.user_input'].sudo().search_count([
            ('partner_id','child_of',[request.env.user.commercial_partner_id.id])
        ])
        values.update({
        'custom_survey_user_input_count': survey_user_input_count,
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        values['custom_survey_user_input_count'] = request.env['survey.user_input'].sudo().search_count([
            ('partner_id','child_of',[request.env.user.commercial_partner_id.id])
        ])
        return values

    @http.route([
        '''/custom_my/survey_user_inputs''',
        '''/custom_my/survey_user_inputs/page/<int:page>'''], type='http', auth="user", website=True)
    def custom_my_survey_user_inputs(self, page=1, groupby='survey', **post):
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'survey': {'input': 'survey', 'label': _('Survey')},
        }

        # default group by value
        if not groupby:
            groupby = 'none'

        domain = [('partner_id','child_of',[request.env.user.commercial_partner_id.id])]
        survey_user_input_count = request.env['survey.user_input'].sudo().search_count([])
        pager = portal_pager(
            url="/custom_my/survey_user_inputs",
            url_args={},
            total=survey_user_input_count,
            page=page,
            step=self._items_per_page
        )
        survey_user_input_ids = request.env['survey.user_input'].sudo().search(
            domain,
            order='id desc',
            limit=self._items_per_page,
            offset=pager['offset']
        )

        if groupby == 'survey':
            grouped_survey_user_input = [request.env['survey.user_input'].concat(*g) for k, g in groupbyelem(survey_user_input_ids, itemgetter('survey_id'))]
        else:
            grouped_survey_user_input = [survey_user_input_ids]

        values={
            'grouped_survey_user_input': grouped_survey_user_input,
            'survey_user_input_ids': survey_user_input_ids,
            'page_name': 'survey_user_input_page',
            'default_url': '/custom_my/survey_user_inputs',
            'pager': pager,
            'searchbar_groupby': searchbar_groupby,
            'groupby': groupby,
        }
        return request.render("survey_portal_odoo.display_survey_user_inputs_custom",values)

    @http.route(['/custom_my/survey_user_inputs/<int:survey_user_input_id>'], type='http', auth="user", website=True)
    def custom_portal_survey_user_inputs(self, survey_user_input_id, **kw):
        if survey_user_input_id:
            survey_user_input_id = request.env['survey.user_input'].sudo().browse(survey_user_input_id)
        else:
            survey_user_input_id = request.env['survey.user_input']
        values = {
            'survey_user_input_id': survey_user_input_id,
            'page_name': 'survey_user_input_page',
        }
        return request.render(
            "survey_portal_odoo.display_survey_user_input_custom",
            values
        )