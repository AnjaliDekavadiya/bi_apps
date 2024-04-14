# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _get_default_stage_id(self):
        """ Gives minimum sequence stage """
        stages =  self.env['custom.sale.order.stage'].search([],order="sequence, id desc", limit=1).id
        return stages

    
    custom_stage_id = fields.Many2one(
        'custom.sale.order.stage',
        string="Stage",
        ondelete='restrict',
        tracking=True, 
        index=True,
        default=_get_default_stage_id, 
        copy=False
    )
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: