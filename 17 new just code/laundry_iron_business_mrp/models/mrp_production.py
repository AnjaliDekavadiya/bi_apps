# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
   
    custom_laundry_request_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry Request',
        copy=False,
    )
    custom_mrpline_id = fields.Many2one(
        'laundry.mrp.line',
        string='Laundry MRP Line',
        copy=False,
    )

    # @api.model
    # def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        # res = super(MrpProduction, self).create(vals)
        res = super(MrpProduction, self).create(vals_list)
        for value in vals_list:
            # if 'custom_mrpline_id' in vals:
            if 'custom_mrpline_id' in value:
                custom_mrp_line = res.custom_mrpline_id
                custom_mrp_line.write({'mrp_id': res.id})
        return res

    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
