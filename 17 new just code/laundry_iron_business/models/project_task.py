# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from odoo.exceptions import UserError, Warning
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"
    
    laundry_ticket_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry Request',
        readonly=True,
        copy=False,
    )
    laundry_task_type = fields.Selection(
        selection= [
            ('diagnosys', 'Diagnosys'),
            ('work_order', 'Work Order'),
        ],
        string="Type",
        readonly = True,
    )
    laundry_service_estimation_line_ids = fields.One2many(
       'laundry.service.estimation.lines',
       'task_id',
       string="Laundry Service Lines"
    )
    cosume_part_ids = fields.One2many(
      'laundry.product.consume.part',
      'laundry_id',
      string="Product Consume Part"
    )
    nature_of_service_ids = fields.Many2many(
        'laundry.service.type.custom',
        string='Services',
    )

    def show_quotation(self):
        for rec in self:
            res = self.env.ref('sale.action_quotations')
            res = res.sudo().read()[0]
            res['domain'] = str([('laundry_task_id','=', rec.id)])
        return res
    
    def create_quotation(self):
        for rec in self:
            if not rec.laundry_service_estimation_line_ids:
                raise UserError(_('Please add Estimation detail to create quotation!'))
            vales = {
                'laundry_task_id': rec.id,
                'partner_id': rec.partner_id.id,
                'user_id': rec.user_id.id,
                'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            }
            order_id = self.env['sale.order'].sudo().create(vales)
            order_id.onchange_partner_id()

            for line in rec.laundry_service_estimation_line_ids:

                if not line.product_id:
                    raise UserError(_('Product not defined on Laundry Service Lines!'))
                
                price_unit = line.price
                if order_id.pricelist_id:
                    price_unit, rule_id = order_id.pricelist_id.get_product_price_rule(
                        line.product_id,
                        line.qty or 1.0,
                        order_id.partner_id
                    )
                
                orderlinevals = {
                    'order_id' : order_id.id,
                    'product_id' : line.product_id.id,
                    'product_uom_qty' : line.qty,
                    'product_uom' : line.product_uom.id,
                    'price_unit' : price_unit,
                    'name' : line.notes or '',
                }
                line_id = self.env['sale.order.line'].create(orderlinevals)
                line_id.product_id_change()
        action = self.env.ref('sale.action_quotations')
        result = action.sudo().read()[0]
        result['domain'] = [('id', '=', order_id.id)]
        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
