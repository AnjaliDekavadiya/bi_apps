# -*- coding: utf-8 -*-

from odoo import models, fields


class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"

    requisition_type = fields.Selection(
        selection_add = [
            ('manufacturing','Manufacturing Order'),
        ],
        ondelete={'manufacturing': 'cascade'}
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: