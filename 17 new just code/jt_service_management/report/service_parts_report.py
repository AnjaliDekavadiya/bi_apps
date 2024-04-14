# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _, tools


class SparepartReport(models.Model):
    _name = 'service.parts.report'
    _description = "Spare Part Report"
    _auto = False

    @api.depends('quantity_need', 'product_id')
    def _compute_quantity(self):
        for rec in self:
            rec.quantity = rec.quantity_need - rec.product_id.virtual_available

    @api.depends('quantity_need')
    def _compute_search_ids(self):
        for rec in self:
            rec.search_ids = []
        print('my compute')

    def _search_ids_search(self, operator, operand):
        service_parts_ids = self.env['service.parts.report'].search([('vendor_id', '!=', False)]).filtered(lambda l: l.quantity > 0)
        return [('id', 'in', service_parts_ids.ids)]

    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string="Quantity", compute='_compute_quantity')
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    quantity_need = fields.Float(string="Quantity Need")
    search_ids = fields.Char(compute="_compute_search_ids", search='_search_ids_search')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'service_parts_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW service_parts_report AS (
            SELECT
                MAX(line.id) AS id,
                SUM(line.quantity) AS quantity_need,
                line.product_id AS product_id,
                (
                    SELECT si.partner_id
                    FROM product_supplierinfo si
                    WHERE si.product_tmpl_id = p.product_tmpl_id
                    ORDER BY sequence
                    LIMIT 1
                ) AS vendor_id
                FROM
                    service_parts_info_one line
                    JOIN product_product p ON line.product_id = p.id
                    JOIN crm_claim sc ON sc.id = line.new_part_id
                WHERE
                    sc.stage IN ('new', 'logged', 'in_diagnosis', 'diagnosed', 'waiting_for_spares')
                    AND p.active = True
                GROUP BY
                    line.product_id, p.product_tmpl_id
            )""")

    def auto_create_po(self):
        
        Orderpoint = self.env['stock.warehouse.orderpoint']
        Tax = self.env['account.tax']
        Product = self.env['product.product']
        FiscalPosition = self.env['account.fiscal.position']
        PurchaseOrderLine = self.env['purchase.order.line']

        records = self.browse(self.env.context.get('active_ids', []))
        for vendor in records.mapped('vendor_id'):
            product_ids = records.filtered(lambda p: p.vendor_id.id == vendor.id).product_id.filtered(lambda p: p.purchase_ok == True)
            purchase_vals = {'is_service_po' :True}

            # update_line_check = self.update_po_ids.filtered(lambda x:x.flag)
            currency_id = vendor.with_context(with_company=self.env.user.company_id.id).property_purchase_currency_id or self.env.user.company_id.currency_id
            
            fpos =  FiscalPosition.with_context(with_company=self.env.user.company_id.id).map_tax(vendor.property_account_position_id)
            
            purchase_vals = {
                'partner_id': vendor.id,
                'date_order': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'date_planned': fields.Datetime.now(),
                'currency_id' : currency_id.id,
                'is_service_po' : True,
            }
            order_lines = []

            for product in product_ids:
                order_point = Orderpoint.search([('company_id','=',self.env.user.company_id.id),('product_id.id','=',product.id)],limit=1)
                product_max_qty = 0
                if order_point:
                    if order_point.product_min_qty >= product.virtual_available:
                        product_max_qty = order_point.product_max_qty - product.virtual_available
                elif product.virtual_available <= 0:
                        product_max_qty = abs(sum(records.filtered(lambda p: p.vendor_id.id == vendor.id and p.product_id.id == product.id).mapped('quantity')))
                if product_max_qty > 0:   
                    selere_line_id = product.seller_ids.filtered(lambda x: x.partner_id.id==vendor.id)
                    price = selere_line_id and selere_line_id[0].price or 0
                    line_currency_id = selere_line_id and selere_line_id[0].currency_id

                    taxes = product.supplier_taxes_id
                    taxes_id = fpos.map_tax(taxes) if fpos else taxes
                    if taxes_id:
                        taxes_id = taxes_id.filtered(lambda x: x.company_id.id == self.env.user.company_id.id)

                    lines = PurchaseOrderLine.search(
                    [('product_id', '=', product.id),
                     ('state', 'in', ['purchase', 'done']),('order_id.partner_id.id','=',vendor.id)]).sorted(
                    key=lambda l: l.order_id.date_order, reverse=True)

                    if lines:
                        # Get most recent Purchase Order Line
                        last_line = lines[:1]

                        price= product.uom_id._compute_quantity(
                            last_line.price_unit, last_line.product_uom)
                        line_currency_id = last_line.order_id.currency_id

                    price_unit = Tax._fix_tax_included_price_company(price, product.supplier_taxes_id, taxes_id, self.env.user.company_id)
                    if price_unit and line_currency_id and currency_id and line_currency_id != currency_id:
                        price_unit = line_currency_id._convert(
                            price_unit, currency_id, self.env.user.company_id, fields.Date.today())
            
                    product_lang = product.with_context({
                        'lang': vendor.lang,
                        'partner_id': vendor.id,
                    })
                    name = product_lang.display_name
                    if product_lang.description_purchase:
                        name += '\n' + product_lang.description_purchase
                    
                    
                    line_vals = {
                        'product_id' : product.id,
                        'name' : name,
                        'date_planned' : fields.Datetime.now(),
                        'product_uom': product.uom_id.id,
                        'product_qty' : product_max_qty,
                        'price_unit' : price_unit,
                        'taxes_id': [(6, 0, taxes_id.ids)]
                    }
                    order_lines.append((0,0,line_vals))
                
            if order_lines:
                purchase_vals.update({'order_line':order_lines})
                purchase_order = self.env['purchase.order'].create(purchase_vals)
