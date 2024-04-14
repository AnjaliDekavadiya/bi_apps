'''
Created on Apr 15, 2020

@author: Zuhair Hammadi
'''
from odoo import models, _
import json

class Project(models.Model):
    _inherit = 'project.project'
    
    def _plan_get_stat_button(self):
        res = super(Project, self)._plan_get_stat_button()
        action = self.analytic_account_id.action_project_costing()
        res.append({
            'name' : _('Costing'),
            'icon' : 'fa-usd',
            'action' : {
                'data-model' : action['res_model'],
                'data-views' : json.dumps(action['views']),
                'data-res-id' : action['res_id']                
                }
            })
        return res