'''
Created on Oct 27, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HrContributionRegister(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Contribution Register'

    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Partner')
    name = fields.Char(required=True)
    register_line_ids = fields.One2many('hr.payslip.line', 'register_id',
        string='Register Line', readonly=True)
    note = fields.Text(string='Description')
