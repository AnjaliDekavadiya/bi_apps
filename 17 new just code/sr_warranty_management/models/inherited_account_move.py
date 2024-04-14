# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, fields, models, _

# inherited account move class.


class AccountMove(models.Model):
    _inherit = "account.move"

    warranty_id = fields.Many2one("sr.product.warranty")
    warranty_count = fields.Integer(
        string="Warranty Count", compute="_get_warranty")
    is_warranty = fields.Boolean("#is Warranty")

    # Warranty count function
    def _get_warranty(self):
        self.warranty_count = self.env["sr.product.warranty"].search_count(
            [("invoice_id", "=", self.id)]
        )

    # Open warranty view action function
    def action_warranty_view(self):
        return {
            "name": "Warranty",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sr.product.warranty",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("invoice_id", "=", self.id)],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: