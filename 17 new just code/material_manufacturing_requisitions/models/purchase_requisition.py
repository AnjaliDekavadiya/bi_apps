# -*- coding: utf-8 -*-


from odoo import models, fields, api


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    is_production_created = fields.Boolean(
        string="IS Production Created ?",
        copy=False,
    )

    #@api.multi
    def show_production(self):
        self.ensure_one()
        action = self.env.ref('mrp.mrp_production_action').sudo().read()[0]
        action['domain'] = [('requisition_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
