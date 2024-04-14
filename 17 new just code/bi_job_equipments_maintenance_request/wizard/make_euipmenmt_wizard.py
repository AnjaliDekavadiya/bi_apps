# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
    
class make_euipment_request_wizard (models.TransientModel):
	_name = 'make.euipment.request.wizard'
	_description = "Make Euipment Request Wizard"

	name = fields.Char('Name')
	maintainance_euipment_id = fields.Many2one('equipment.equipment', 'Maintainance Equipment Machine')
	maintainance_team_id = fields.Many2one('crm.team', string='Maintainance Team')
	priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority')
	schedule_date = fields.Datetime('Schedule Time')
	duration = fields.Integer('Duration')
	maintainance_type_id = fields.Many2one('maintainance.type','Maintainance Type')
	notes = fields.Text('Notes')  
	category_id = fields.Many2one('equipment.category','Equipment Category')  

    
	def create_equipment(self):
		equipment_request_id =self.env['equipment.request'].create({
											'name': self.name,
                                             'equipment_id': self.maintainance_euipment_id.id,
                                              'maintainance_team_id':self.maintainance_team_id.id,
                                             'priority': self.priority,
                                             'schedule_date': self.schedule_date,
                                             'request_date': datetime.now().date(),
                                             'duration': self.duration,
                                             'category_id': self.category_id.id,
                                             'maintainance_type_id': self.maintainance_type_id.id,
                                             'notes': self.notes,
                                            'requested_user_id': self.env.uid,
                                            'job_order_id': self._context.get('active_id')})
      
    

