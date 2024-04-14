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

from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProductBrand(models.Model):

    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char("Name", required=True)
    # discount = fields.Float("Woocommerce discount")
    no_stock = fields.Boolean("No stock")
    min_stock_month = fields.Integer("Minimum Stock Month")
    max_stock_month = fields.Integer("Maximum Stock Month")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand')
    comp_list_price = fields.Float(compute='_product_currency_in_company', string='Sale Price (AED)')
    spare_part_ids = fields.Many2many('product.product', "product_parts_rel", 'product_id', 'part_id',
                                      string='Spare Part Of')
    cust_currency_id = fields.Many2one('res.currency')
    is_spare_part = fields.Boolean('Is Spare Part?', default=False, copy=False)

    def _product_currency_in_company(self):
        user = self.env.user
        company = user.company_id
        company_currency_id = company.currency_id.id
        res_currency_rate_obj = self.env['res.currency.rate']
        
        for product in self:
            cust_currency_id = product.cust_currency_id.id if product.cust_currency_id else False
            list_price = product.list_price
            
            com_currency_rate = res_currency_rate_obj.search([('currency_id', '=', company_currency_id),
                                                              ('company_id', '=', company.id)], limit=1,
                                                             order='name desc')
            if com_currency_rate and cust_currency_id:
                if cust_currency_id == company_currency_id:
                    product.comp_list_price = list_price
                else:
                    rate = product.cust_currency_id.rate
                    if product.cust_currency_id.additional_per_rate != 0 and product.cust_currency_id.rate != 0:
                        rate = product.cust_currency_id.rate / (1 + (product.cust_currency_id.additional_per_rate / 100))
                    com_sale_price = list_price / rate
                    product.comp_list_price = com_sale_price
            else:
                product.comp_list_price = list_price

    def update_spare_part(self):
        for product in self:
            product.is_spare_part = bool(product.spare_part_ids)

    def write(self, vals):
        print("vals=======", vals)
        context = self._context
        mail_msg_obj = self.env['mail.message']
        brand_obj = self.env['product.brand']
        
        prod_tem_action = self.env.ref('product.product_template_action').id
        inv_prod_tem_action = self.env.ref('stock.product_template_action_product').id
        pur_prod_tem_action = self.env.ref('purchase.product_normal_action_puchased').id
        mrp_prod_tem_action = self.env.ref('mrp.product_template_action').id

        if 'list_price' in vals:
            for product in self:
                msg = f"<ul><li>Sale Price: {product.list_price} -> {vals.get('list_price')}</li></ul>"
                mail_msg_obj.create({'model': 'product.template', 'res_id': product.id, 'body': msg})

        if context.get('params') and context.get('params').get('action'):
            action = context.get('params').get('action')
            if 'brand_id' in vals:
                if (not action) or (action and action not in [prod_tem_action, inv_prod_tem_action, pur_prod_tem_action,
                                                               mrp_prod_tem_action]):
                    vals.pop('brand_id')
                    for product in self:
                        is_msg = False
                        msg = ''
                        if vals.get('brand_id') and vals.get('list_price'):
                            brand = brand_obj.browse(vals.get('brand_id'))
                            old_brand = product.brand_id.name if product.brand_id else ''
                            msg = f"<ul><li>Brand: {old_brand} -> {brand.name}</li><li> Sale Price: {product.list_price} -> {vals.get('list_price')}</li></ul>"
                            is_msg = True
                        elif vals.get('brand_id') and not vals.get('list_price'):
                            brand = brand_obj.browse(vals.get('brand_id'))
                            old_brand = product.brand_id.name if product.brand_id else ''
                            msg = f"<ul><li>Brand: {old_brand} -> {brand.name}</li></ul>"
                            is_msg = True
                        elif vals.get('list_price') and not vals.get('brand_id'):
                            msg = f"<ul><li>Sale Price: {product.list_price} -> {vals.get('list_price')}</li></ul>"
                            is_msg = True
                        if is_msg:
                            mail_msg_obj.create({'model': 'product.template', 'res_id': product.id, 'body': msg})

        res = super(ProductTemplate, self).write(vals)
        print("resssssssssssssssssssssssss", res)
        return res

    def set_min_max(self):
        today = datetime.today().date()
        year_ago = today - relativedelta(years=1)
        domain = [
            ('product_id.seller_ids', '!=', False),
            ('order_id.date_order', '>=', year_ago),
            ('order_id.date_order', '<=', today),
            ('product_id.type', '=', 'product'),
            ('product_id.is_spare_part', '=', True)
        ]

        sale_location_ids = self.env['sale.order.line'].search(domain).mapped('order_id.warehouse_id.out_type_id.default_location_src_id')
        service_location_ids = self.env['service.parts.info.one'].search([('product_id.seller_ids', '!=', False)]).mapped('new_part_id.service_center_id.source_location_id')
        location_ids = sale_location_ids + service_location_ids
        location_ids = tuple(set(location_ids))

        for location_id in location_ids:
            warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', location_id.company_id.id)], limit=1)
            location_id = self.env['stock.location'].browse(location_id.id)

            domain = [
                ('product_id.seller_ids', '!=', False),
                ('order_id.warehouse_id.out_type_id.default_location_src_id', '=', location_id.id),
                ('order_id.date_order', '>=', year_ago),
                ('order_id.date_order', '<=', today),
                ('product_id.type', '=', 'product'),
                ('product_id.is_spare_part', '=', True)
            ]

            service_line_ids = self.env['service.parts.info.one'].search([
                ('product_id.seller_ids', '!=', False),
                ('new_part_id.service_center_id.source_location_id', '=', location_id.id)
            ])

            sale_line_ids = self.env['sale.order.line'].search(domain)
            product_id_sale = sale_line_ids.mapped('product_id').ids
            product_id_service = service_line_ids.mapped('product_id').ids
            product_ids = product_id_sale + product_id_service
            product_ids = tuple(set(product_ids))

            for product_id in product_ids:
                product_id = self.env['product.product'].browse(product_id)
                year_sale = sum(x.product_uom_qty for x in sale_line_ids.filtered(lambda a: a.product_id.id == product_id.id))
                live_need = sum(x.quantity for x in service_line_ids.filtered(lambda a: a.product_id.id == product_id.id))
                vendor_id = False
                minimum_required = 0
                maximum_required = 0

                if product_id.seller_ids:
                    vendor_ids = product_id.seller_ids
                    if vendor_ids:
                        vendor_id = vendor_ids[0].name

                if vendor_id:
                    minimum_required = round(year_sale / 12) * vendor_id.min_month_sparepart
                    maximum_required = round(year_sale / 12) * vendor_id.max_month_sparepart

                if live_need > minimum_required:
                    minimum_required = live_need

                if live_need > maximum_required:
                    maximum_required = live_need

                if minimum_required > 0 and maximum_required > 0:
                    order_point = self.env['stock.warehouse.orderpoint'].search([
                        ('product_id.id', '=', product_id.id),
                        ('company_id', '=', location_id.company_id.id),
                        ('location_id', '=', location_id.id)], limit=1)

                    if order_point:
                        print("calll order exist")
                        order_point.product_min_qty = minimum_required
                        order_point.product_max_qty = maximum_required
                    else:
                        print("calll order new")
                        if warehouse_id:
                            order_point = self.env['stock.warehouse.orderpoint'].create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'company_id': location_id.company_id.id,
                                'warehouse_id': warehouse_id.id,
                                'location_id': location_id.id,
                                'product_min_qty': minimum_required,
                                'product_max_qty': maximum_required,
                            })


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    spare_part_ids = fields.Many2many(related="product_id.spare_part_ids", string='Spare Part Of')
    is_spare_part = fields.Boolean(related="product_id.is_spare_part", string='Is Spare Part?')
