# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class ProjectTask(models.Model):
    _inherit = 'project.task'

    waste_management_ids = fields.One2many(
        'construction.waste.management', 
        'task_id', 
        string='Waste Management',
        copy=False,
    )

    # @api.multi
    def action_open_scrap(self):
        self.ensure_one()
        # action = self.env.ref('stock.action_stock_scrap').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_stock_scrap')
        action['domain'] = [('custom_task_id', '=', self.id)]
        return action
    
    # @api.multi
    def action_open_stock_picking(self):
        self.ensure_one()
        # action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('custom_task_id','=', self.id)]
        return action