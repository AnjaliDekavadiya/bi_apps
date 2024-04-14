# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LaundryBusinessService(models.Model):
    _inherit = 'laundry.business.service.custom'
   
    mrp_line_ids = fields.One2many(
        'laundry.mrp.line',
        'laundry_service_request_id',
        string='Manufactring Lines',
        copy=True,
    )
    
    def show_laundry_mrp(self):
        self.ensure_one()
        res = self.env.ref('mrp.mrp_production_action')
        res = res.sudo().read()[0]
        res['domain'] = str([('custom_laundry_request_id', '=', self.id)])
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
