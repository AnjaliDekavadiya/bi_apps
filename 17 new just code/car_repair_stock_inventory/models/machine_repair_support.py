# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api, _

class CarRepairSupport(models.Model):
    _inherit = 'car.repair.support'

    #@api.multi
    def show_move_lines(self):
        self.ensure_one()
        # action = self.env.ref('stock.stock_move_action').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('stock.stock_move_action')
        action['domain'] = str([('car_repair_request_id', '=', self.id)])
        action['context'] = {'search_default_done': 0, 'search_default_groupby_location_id': 0}
        return action

    #@api.multi
    def show_picking_repair_show(self):
        self.ensure_one()
        # action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('stock.action_picking_tree_all')
        move = self.env['stock.move'].search([('car_repair_request_id','=',self.id)])
        stock_ref = move.mapped('picking_id')
        action['domain'] = [('id', 'in', stock_ref.ids)]
        return action
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
