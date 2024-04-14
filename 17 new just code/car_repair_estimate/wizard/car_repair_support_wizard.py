# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CarRepairSupportWizard(models.TransientModel):
    _name = 'car.repair.support.wizard'
    _description = 'Car Repair Support Wizard'

    # @api.multi #odoo13
    def create_estimate(self):
        return {
            'view_mode': 'form',
            'view_id': self.env.ref(
                'odoo_sale_estimates.view_sale_estimate_form').ids,
            'res_model': 'sale.estimate',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
