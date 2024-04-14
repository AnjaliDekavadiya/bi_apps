# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class HelpdeskSupport(models.Model):
    _inherit = "helpdesk.support"
    
    # @api.multi
    def create_ticket_partner_survey(self):
        partner_ids = self.mapped("partner_id")
        action_survey = partner_ids.create_partner_survey()
        return action_survey

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
