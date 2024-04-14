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

# Inherited stock picking class.


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super(StockPicking, self).button_validate()
        if self.sale_id and self.state == 'done':
            self.sale_id.create_warranty_records(self.sale_id)
        if self.move_ids_without_package:
            for line in self.move_ids_without_package:
                warranty_id = self.env["sr.product.warranty"].search(
                    [
                        ("product_id", "=", line.product_tmpl_id.id),
                        ("sale_order_id", "=", self.origin),
                    ]
                )
                if warranty_id:
                    for lot in line.lot_ids:
                        warranty_id.serial_number = lot.name
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: