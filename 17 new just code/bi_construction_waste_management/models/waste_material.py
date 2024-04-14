# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class WasteMaterial(models.Model):
	_name = 'waste.material'
	_description = 'Waste Material'

	name = fields.Char(string='Sequence', readonly=True)
	waste_method = fields.Selection([('Reuse Material','Reuse Material'),('Scrap Material','Scrap Material')],string = 'Waste Material')
	product_id = fields.Many2one('product.product',string='product')
	quantity = fields.Float(default=1.0,string="Quantity")
	uom_id = fields.Many2one('uom.uom',string='Unit Of Measure')
	source_location_id = fields.Many2one('stock.location',string='Source Location')
	destination_location_id = fields.Many2one('stock.location',string='Destination Location')
	picking_type_id = fields.Many2one('stock.picking.type',string='Picking Type')
	job_waste_id = fields.Many2one('job.order',string='Job Material Requisition')
	check_waste = fields.Boolean(default=False)

	def _valid_field_parameter(self,field,name):
		return name == 'defalut' or super()._valid_field_parameter(field,name)
     

	@api.onchange('product_id')
	def onchange_waste_product_id(self):
		res = {}
		if not self.product_id:
			return res
		self.uom_id = self.product_id.uom_id.id

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			if vals.get('name', _('New')) == _('New'):
				vals['name'] = self.env['ir.sequence'].next_by_code('waste.seq') or _('New')

		#vals['name'] =self.env['ir.sequence'].get('waste.material')
		return super(WasteMaterial, self).create(vals_list)

	def create_scrap_picking(self):
		waste_obj = self.job_waste_id
		if self.waste_method =="Scrap Material":
			scrap_obj = self.env['stock.scrap']
			scrap_details = {
							'product_id' : self.product_id.id,
							'scrap_qty' : self.quantity,
							'product_uom_id' : self.uom_id.id,
							'waste_scrap_id' : self.id,
							'job_scrap_id' : waste_obj.id
							}
			self.check_waste = True
			res = scrap_obj.create(scrap_details)
		else:
			invent_obj = self.env['stock.picking']
			stock_move_obj = self.env['stock.move']
			pick_details = {
							'partner_id' :self.env.user.partner_id.id,
							'material_requisition_id' : waste_obj.id,
							'picking_type_id' : self.picking_type_id.id,
							'location_id':self.source_location_id.id,
							'location_dest_id' : self.destination_location_id.id,
							'waste_stock_id' :self.id,
							'job_stock_id' : waste_obj.id,
							}
			self.check_waste = True
			res = invent_obj.create(pick_details)
			product_details  =  {
                                'name': self.product_id.name,
                                'product_id' : self.product_id.id,
                                'product_uom_qty' : self.quantity,
                                'product_uom' : self.uom_id.id,
                                'picking_id' : res.id,
                                'location_id': self.source_location_id.id,
                                'location_dest_id' : self.destination_location_id.id

                }
			stock_move_obj.create(product_details)

class JobOrderInherited(models.Model):
	_inherit = 'job.order'

	wastematerial_ids = fields.One2many('waste.material','job_waste_id',string='waste material ids')
	scrap_count = fields.Integer('Scrap', compute='_get_scrap_count')
	internal_picking_count = fields.Integer('Internal Picking', compute='_get_internal_picking_count')

	def _get_scrap_count(self):
		for scrap in self:
			scrap_ids = self.env['stock.scrap'].search([('job_scrap_id','=',scrap.id)])
			scrap.scrap_count = len(scrap_ids)

	def scrap_button(self):
		self.ensure_one()
		return {
			'name': 'Scrap',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'stock.scrap',
			'domain': [('job_scrap_id', '=', self.id)],
		}        

	def _get_internal_picking_count(self):
		for picking in self:
			picking_ids = self.env['stock.picking'].search([('job_stock_id','=',picking.id)])
			picking.internal_picking_count = len(picking_ids)

	def internal_picking_button(self):
		self.ensure_one()
		return {
			'name': 'Internal picking',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'stock.picking',
			'domain': [('job_stock_id', '=', self.id)],
		}        

class InheritedStockPicking(models.Model):
	_inherit = 'stock.picking'

	waste_stock_id = fields.Many2one('waste.material','Waste Material')
	job_stock_id = fields.Many2one('job.order','Job order ')

class InheritedStockScrap(models.Model):
	_inherit = 'stock.scrap'

	waste_scrap_id = fields.Many2one('waste.material','Waste Material')
	job_scrap_id = fields.Many2one('job.order','Job Order')