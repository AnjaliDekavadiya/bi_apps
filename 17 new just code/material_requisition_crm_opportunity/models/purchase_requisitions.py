# -*- coding: utf-8 -*-

from odoo import models, fields , api

class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    custom_crm_lead_id = fields.Many2one(
        'crm.lead',
        string='Lead / Opportunity',
        readonly=True
    )

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
