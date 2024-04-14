# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # @api.multi #odoo13
    def view_repair_requests(self):
        self.ensure_one()
        # action = self.env.ref('machine_repair_management.action_machine_repair_support').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('machine_repair_management.action_machine_repair_support')
        action['domain'] = [('task_id', '=', self.id)]
        return action

