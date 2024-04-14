'''
Created on Apr 2, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class Employee(models.Model):
    _inherit = "hr.employee"
    
    peers_ids = fields.Many2many('hr.employee', string='Peers (Same Manger)', compute = '_calc_peers_ids')
    department_peers_ids = fields.Many2many('hr.employee', string='Peers (Same Department)', compute = '_calc_department_peers_ids')
    himself_id = fields.Many2one('hr.employee', string='Employee (himself)', compute = '_calc_himself_id')

    @api.depends('parent_id')
    def _calc_peers_ids(self):
        for record in self:
            record.peers_ids = self.env['hr.employee'].search([('parent_id','=', record.parent_id.id),('id','!=', record.id)])
            
    @api.depends('department_id')
    def _calc_department_peers_ids(self):
        for record in self:
            record.department_peers_ids = self.env['hr.employee'].search([('department_id','=', record.department_id.id),('id','!=', record.id)])
                                    
    def _calc_himself_id(self):
        for record in self:
            record.himself_id = record