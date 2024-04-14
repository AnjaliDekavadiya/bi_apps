# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"
    
    # @api.multi
    def create_partner_survey(self):
        self.ensure_one()
        # action = self.env.ref('survey.action_survey_form').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_form')
        action['domain'] = [('ticket_partner_id', 'child_of', self.id)]
        action['context'] = {'default_ticket_partner_id': self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
