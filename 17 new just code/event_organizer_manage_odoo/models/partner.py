# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    def action_event_organizor_partner_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('event.action_event_view')
        action['domain'] = [('partner_custom_id','child_of', [self.id])]
        return action