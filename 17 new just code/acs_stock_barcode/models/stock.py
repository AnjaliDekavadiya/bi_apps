# -*- encoding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        ProductObj = self.env['product.product']
        LotObj = self.env['stock.lot']
        Line = self.env['stock.move']

        if barcode and self.state=='draft':
            #Check first Lot
            lot = LotObj.search([('name','=',barcode)], limit=1)
            if lot:
                product = lot.product_id
            else:
                product = ProductObj.search([('barcode','=',barcode)], limit=1)
                if not product:
                    product = ProductObj.search([('default_code','=',barcode)], limit=1)
                if not product:
                    raise UserError(_('There is no product with Lot, Barcode or Reference: %s') % (barcode))

            flag = 1
            for o_line in self.move_ids_without_package:
                if o_line.product_id == product:
                    o_line.product_uom_qty += 1
                    o_line.quantity += 1
                    flag = 0
            if flag:
                self.move_ids_without_package += Line.new({
                    'product_id': product.id,
                    'product_uom_qty' : 1,
                    'quantity' : 1,
                    'name': product.name,
                    'product_uom': product.uom_id.id,
                    'state': 'draft',
                    'picking_type_id': self.picking_type_id and self.picking_type_id.id or False,
                    'location_id': self.location_id and self.location_id.id or False,
                    'location_dest_id': self.location_dest_id and self.location_dest_id.id or False,
                })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 