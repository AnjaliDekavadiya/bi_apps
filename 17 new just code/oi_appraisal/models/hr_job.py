'''
Created on Nov 12, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class Job(models.Model):
    _inherit = "hr.job"

    appraisal_template_ids = fields.Many2many('appraisal.template', string='Appraisal Template')
    