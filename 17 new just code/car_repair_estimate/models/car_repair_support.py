# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CarRepairSupport(models.Model):
    _inherit = 'car.repair.support'

    car_estimate_count = fields.Integer(
        compute='_compute_estimate_counter',
        string="Car Estimation Count"
    )

    def _compute_estimate_counter(self):
        for rec in self:
            rec.car_estimate_count = self.env['sale.estimate'].search_count(
                [('custom_car_repair_id', 'in', rec.ids)])

    # @api.multi #odoo13
    def view_estimates(self):
        self.ensure_one()
        # for rec in self:
            # action = self.env.ref(
            #     'odoo_sale_estimates.action_estimate').sudo().read()[0]
            # action['domain'] = [('custom_car_repair_id', 'in', rec.ids)]
        action = self.env['ir.actions.actions']._for_xml_id('odoo_sale_estimates.action_estimate')
        action['domain'] = [('custom_car_repair_id', '=', self.id)]
        return action
   