from odoo import fields,models,api

class jobposition(models.Model):
    _name = 'tailoring.job'
    _description = 'tailoring_job'
    _rec_name = 'job_name'

    job_name = fields.Char(string="Job Positions")