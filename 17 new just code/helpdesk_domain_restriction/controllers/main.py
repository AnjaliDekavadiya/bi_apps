# -*- coding: utf-8 -*-


from odoo import http, _
from odoo.http import request
from odoo import models,registry, SUPERUSER_ID
from odoo.addons.website_helpdesk_support_ticket.controllers.main import HelpdeskSupport


class HelpdeskSupport(HelpdeskSupport):

    def _check_domain(self, **post):
        domain_name = post['email'].split("@")[1]
        helpdesk_domain_ids = request.env['helpdesk.domain'].sudo().search([('name', '=', domain_name)])
        if helpdesk_domain_ids:
            return False
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
