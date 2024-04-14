# -*- coding: utf-8 -*

from odoo import models, fields, api

class JobCosting(models.Model):
    _inherit = 'job.costing'

    #@api.multi
    def action_open_construction_task_ticket(self):
        # for rec in self:
        self.ensure_one()
        # action = self.env.ref('construction_contracting_issue_tracking.action_construction_ticket')
        # action = action.sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('construction_contracting_issue_tracking.action_construction_ticket')
        action['domain'] = str([('jobcost_sheet_id','=',self.id)])
        return action
