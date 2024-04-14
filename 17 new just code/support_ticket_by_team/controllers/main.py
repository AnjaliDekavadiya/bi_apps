# -*- coding: utf-8 -*-

import base64
from odoo import http, _
from odoo.http import request
from odoo.addons.website_helpdesk_support_ticket.controllers.main import CustomerPortal, HelpdeskSupport
from odoo.addons.portal.controllers.portal import CustomerPortal as website_account

#from odoo.addons.website_job_workorder_request.controllers.main import website_account as JoborderController

class HelpdeskSupport(HelpdeskSupport):
    
    @http.route(['/page/helpdesk_support_team'], type='http', auth='public', website=True)
    def get_helpdesk_team(self, **kw):
        team_obj = request.env['support.team']
        support_teams = team_obj.sudo().search([])
        values = {
            'team_ids': support_teams,
        }
        return request.render('support_ticket_by_team.template_helpdesk_teams_kanban',values)

    @http.route('''/team_detail/<model("support.team"):team>''', type='http', auth='public', website=True)
    def team_detail_form(self, team):
        values = {
            'team': team,
        }
        return request.render('support_ticket_by_team.template_helpdesk_team_detail_form',values)
    
    @http.route('''/create/ticket/<model("support.team"):team>''', type='http', auth='public', website=True)
    def create_ticket_from_team(self, team):
        values = {
            'team': team,
        }
        return request.render('website_helpdesk_support_ticket.website_helpdesk_support_ticket',values)

