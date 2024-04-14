# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # @api.multi
    def write(self, vals):
        print('-------------self------',vals)
        if vals.get('project_id'):
            project_id = vals['project_id']
            print('project_id-----------',project_id)
        else:
            project_id = self.project_id.id
        # if vals.get('stage_id') and vals['stage_id'] and not vals.get('user_id'):
        if vals.get('stage_id') and vals['stage_id']:
            project_id = self.env['project.project'].browse(project_id)
            print('--------------------------project_id---------',project_id)
            project_stage_security = project_id.project_stage_security_ids
            print('--------------stage---------',project_stage_security)
            for security in project_stage_security:
                if security.user_id and vals.get('stage_id') == security.stage_id.id:
                    # vals.update(user_id=security.user_id.id)
                    vals.update(user_ids=[(4, security.user_id.id)])
                if security.group_ids and vals.get('stage_id') == security.stage_id.id:
                    flag = False
                    for group in security.group_ids:
                        print('--------------security--------',security)
                        if self.env.user.id in group.users.ids:
                            flag = True
                        if not flag:
                            raise ValidationError('You are not allowed to move this task to next stage.')
        return super(ProjectTask, self).write(vals)
        
#class ProjectIssue(models.Model):
    #_inherit = 'project.issue'
    
    #@api.multi
    #def write(self, vals):
        #if vals.get('project_id'):
            #project_id = vals['project_id']
        #else:
            #project_id = self.project_id.id
        #if vals.get('stage_id') and vals['stage_id'] and not vals.get('user_id'):
            #project_id = self.env['project.project'].browse(project_id)
            #project_stage_security = project_id.project_stage_security_ids
            #for security in project_stage_security:
                #if security.user_id and vals.get('stage_id') == security.stage_id.id:
                    #vals.update(user_id=security.user_id.id)
                #if security.group_ids and vals.get('stage_id') == security.stage_id.id:
                    #flag = False
                    #for group in security.group_ids:
                        #if self.env.user.id in group.users.ids:
                            #flag = True
                        #if not flag:
                            #raise ValidationError('You are not allowed to move this issue to next stage.')
        #return super(ProjectIssue, self).write(vals)

