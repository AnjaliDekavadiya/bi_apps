# -*- coding: utf-8 -*-

from odoo import fields, models

class Event(models.Model):
    _inherit = "event.event"

    def action_hr_expense_event_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('hr_expense.hr_expense_actions_my_all')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action
    
