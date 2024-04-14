# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime


class job_order(models.Model):
    _inherit = 'job.order'
     
    euipment_ids = fields.One2many('equipment.equipment', 'job_order_id')
    equipment_request_ids = fields.One2many('equipment.request', 'job_order_id')

    def _get_number_of_euipment(self):
        for order in self:
            list_euipment_ids  = []
            equipment_ids = self.env['equipment.equipment'].search([('job_order_id', '=', self.id)])
            for equipment in equipment_ids:
                list_euipment_ids.append(equipment.id)  
            order.count_of_equipment = len(list_euipment_ids)
    
    def button_view_euipment(self):
        for oder in self:
            list_euipment_ids = []
            equipment_ids = self.env['equipment.equipment'].search([('job_order_id', '=', self.id)])
            for equipment in equipment_ids:
                list_euipment_ids.append(equipment.id)  
        context = dict(self._context or {})
        return {
            'name': _('Equipment'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'equipment.equipment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', list_euipment_ids)],
            'context': context,
        }
                    
    def _get_number_of_euipment_request(self):
        for order in self:
            euipment_request_ids = self.env['equipment.request'].search([('job_order_id', '=', self.id)])            
            order.count_of_equipment_request = len(euipment_request_ids)

    def button_view_equipment_request(self):
        exp_list = []
        exp_ids = self.env['equipment.request'].search([('job_order_id', '=', self.id)])
        for exp in exp_ids:
            exp_list.append(exp.id)
                            
        context = dict(self._context or {})
        return {
            'name': _('Equipment Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'equipment.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', exp_list)],
            'context': context,
        }

    count_of_equipment = fields.Integer('Equipment', compute='_get_number_of_euipment')
    count_of_equipment_request = fields.Integer('Equipment Request', compute='_get_number_of_euipment_request')

class euipment_request(models.Model):
    _name = 'equipment.request'
    _description = "Euipment Request"

    name = fields.Char(string='Name')
    requested_user_id = fields.Many2one('res.users', 'Requested By', default=lambda self: self.env.uid)
    equipment_id = fields.Many2one('equipment.equipment', 'Equipment Machine')
    category_id = fields.Many2one('equipment.category', 'Equipment Category')
    request_date = fields.Datetime('Requested Date', default=datetime.now().date())
    close_date = fields.Date('Close Date')
    maintainance_type_id = fields.Many2one('maintainance.type', 'Maintainance Type')
    maintainance_team_id = fields.Many2one('crm.team')
    resposible_id = fields.Many2one('res.users', 'Resposible')
    schedule_date = fields.Datetime('Schedule Date')
    duration = fields.Integer('Duration')
    notes = fields.Text('Notes')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority')
    state = fields.Selection([('draft', 'Draft'), ('start', 'Start'), ('pause', 'Pause'), ('stop', 'Stop')], default= 'draft')
    job_order_id = fields.Many2one('job.order', 'Job Order')

    def to_start(self):
        for request in self:
            request.state = 'start'

    def to_pause(self):
        for request in self:
            request.state = 'pause'

    def to_restart(self):
        for request in self:
            request.state = 'start'

    def to_finish(self):
        for request in self:
            request.state = 'stop'

class maintainance_type(models.Model):
    _name = 'maintainance.type'
    _description = "Maintainance Type"

    name = fields.Char('Name', required=True)


class equipment_category(models.Model):
    _name = 'equipment.category'
    _description = "Equipment Category"
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')


class equipment(models.Model):
    _name = 'equipment.equipment'
    _description = "Equipment"


    name = fields.Char('Name',required=True)
    equipment_category_id = fields.Many2one('equipment.category')
    model = fields.Char('Model')
    serial_number = fields.Char('Serial Number')
    notes = fields.Text('Notes')
    owner = fields.Many2one('res.users', 'Owner')
    maintainance_team = fields.Many2one('crm.team')
    technician_id = fields.Many2one('res.users', 'Technician')
    assigned_date = fields.Date('Assigned Date')
    scrap_date = fields.Date('Scrap Date')
    used_in_location = fields.Many2one('stock.location', 'Location')
    job_order_id = fields.Many2one('job.order', 'Job Order')
    description = fields.Text('Description')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    supplier_ref = fields.Char('Supplier Reference')
    cost = fields.Float('Cost')
    warranty = fields.Char('Warranty')
    material_request_ids = fields.One2many('equipment.request', 'equipment_id')

    def _get_number_of_request(self):
        for order in self:
            euipment_request_ids = self.env['equipment.request'].search([('equipment_id', '=', self.id)])            
            order.count_of_request = len(euipment_request_ids)
         
    def button_view_request(self):
        exp_list  = []
        exp_ids = self.env['equipment.request'].search([('equipment_id', '=', self.id)])
        for exp in exp_ids:
            exp_list.append(exp.id)
                            
        context = dict(self._context or {})
        return {
            'name': _('Equipment Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'equipment.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', exp_list)],
            'context': context,
        }

    count_of_request = fields.Integer('Request', compute='_get_number_of_request')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
