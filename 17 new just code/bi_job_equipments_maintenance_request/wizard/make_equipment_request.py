# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
    
class make_euipment_wizard (models.TransientModel):
	_name = 'make.euipment.wizard'
	_description = "Make Euipment Wizard"

	name = fields.Char('Name')
	model = fields.Char('Model')
	serial_number = fields.Char('Serial')
	notes = fields.Text('Note')
	equipment_category_id = fields.Many2one('equipment.category', 'Equipment Category')

	def create_equipment(self):
		equipment_id =self.env['equipment.equipment'].create({'name': self.name,
                                             'equipment_category_id': self.equipment_category_id.id,
                                          	 'model': self.model,
                                             'assigned_date':datetime.now(),
                                             'serial_number':self.serial_number,
                                             'notes':self.notes,
                                             'owner':self.env.uid,
                                             'job_order_id': self._context.get('active_id')})
      
    
