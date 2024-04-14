# -*- encoding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']
        
    def on_barcode_scanned(self, barcode):
        if barcode and self.state=='draft':
            LineObj = self.env['sale.order.line']
            ProductObj = self.env['product.product']
            product = ProductObj.search([('barcode','=',barcode)], limit=1)
            if not product:
                product = ProductObj.search([('default_code','=',barcode)], limit=1)
            if not product:
                raise UserError(_('There is no product with Barcode or Reference: %s') % (barcode))

            flag = True
            for o_line in self.order_line:
                if o_line.product_id == product:
                    flag = False
                    o_line.product_uom_qty = o_line.product_uom_qty + 1

            if flag:
                price = product.list_price
                if self.pricelist_id:
                    price = self.pricelist_id._get_product_price(product, 1)
                self.order_line += LineObj.new({
                    'product_id': product.id,
                    'name': product.name,
                    'tax_id': [(6, 0, product.taxes_id.ids)],
                    'product_uom_qty' :  1,
                    'price_unit': price,
                    'product_uom': product.uom_id.id,
                    'state' : 'draft',
                })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: