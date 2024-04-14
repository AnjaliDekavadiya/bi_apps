# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, models
import json
import base64
from odoo.tools import date_utils


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals):
        res = super(ProductProduct,self).create(vals)
        for record in res:
            record.create_product_changes('CREATE','New Product Created')
        return res


    def write(self, vals):
        res = super(ProductProduct,self).write(vals)
        vals_keys = vals.keys()
        description = ','.join(vals_keys)
        vals_keys = set(vals.keys())
        fields = set(self.get_pos_fields())
        comman_fields = fields.intersection(vals_keys)
        if len(comman_fields):
            for record in self:
                if 'sale_ok' in vals.keys():
                    if not vals['sale_ok']:
                        record.create_product_changes('DELETE',"Product Deleted")
                    elif vals['sale_ok'] and record.available_in_pos:
                        record.create_product_changes('UPDATE',description)
                elif 'sale_ok' not in vals.keys() and 'available_in_pos' in vals.keys():
                    if not vals['available_in_pos']:
                        record.create_product_changes('DELETE',description)
                    elif vals['available_in_pos']:
                        record.create_product_changes('UPDATE',description)
                elif record.sale_ok and record.available_in_pos:
                    record.create_product_changes('UPDATE',description)
        return res
    
    def _process_pos_ui_product_product(self, products):
        session = self.env['pos.session']
        categories = session._get_pos_ui_product_category(session._loader_params_product_category())
        product_category_by_id = {category['id']: category for category in categories}
        for product in products:
            product['categ'] = product_category_by_id[product['categ_id'][0]]
    
    def get_pos_fields(self):
        session = self.env['pos.session']
        result = session._loader_params_product_product()
        return result['search_params']['fields']
    
    def create_product_changes(self,operation,description):
        self.ensure_one()
        product_operations = self.env['pos.common.changes'].search([('model_name','=',"product.product"),('record_id','=',self.id),('state','in',['error','draft'])],order="id desc")
        if not len(product_operations):
            data  = self.read(self.get_pos_fields())
            self._process_pos_ui_product_product(data)
            if operation == 'UPDATE':
                self.env['pos.common.changes'].create({
                        'record_id': self.id,
                        'record': json.dumps(data, default=date_utils.json_default),
                        'operation': 'UPDATE',
                        'model_name': "product.product",
                        'description':description,
                        'state': "draft",
                    })
            elif operation == "CREATE":
                self.env['pos.common.changes'].create({
                        'record_id': self.id,
                        'record': json.dumps(data, default=date_utils.json_default),
                        'operation': 'CREATE',
                        'model_name': "product.product",
                        'description':description,
                        'state': "draft",
                    })
            else:
                self.env['pos.common.changes'].create({
                    'record_id': self.id,
                    'record': json.dumps(data, default=date_utils.json_default),
                    'operation': 'DELETE',
                    'model_name': "product.product",
                    'description':description,
                    'state': "draft",
                })


    def unlink(self):
        for record in self:
            if record.sale_ok and record.available_in_pos:
                record.create_product_changes('DELETE',"Product Deleted")
        return super(ProductProduct,self).unlink()


class ProductTemplate(models.Model):
    _inherit = "product.template"
    

    def write(self, vals):
        res = super(ProductTemplate,self).write(vals)
        vals_keys = vals.keys()
        description = ','.join(vals_keys)
        vals_keys = set(vals.keys())
        fields = set(['name', 'display_name', 'list_price', 'standard_price', 'categ_id', 'pos_categ_id', 'taxes_id',
                 'barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description',
                 'product_tmpl_id','tracking', 'write_date', 'available_in_pos', 'attribute_line_ids', 'active'])
        comman_fields = fields.intersection(vals_keys)
        if len(comman_fields):
            for record in self:
                if 'sale_ok' in vals.keys():
                    if not vals['sale_ok']:
                        for variant in record.product_variant_ids:
                            variant.create_product_changes('DELETE',description)
                    elif vals['sale_ok'] and record.available_in_pos:
                        for variant in record.product_variant_ids:
                            variant.create_product_changes('UPDATE',description)
                elif 'sale_ok' not in vals.keys() and 'available_in_pos' in vals.keys():
                    if not vals['available_in_pos']:
                        for variant in record.product_variant_ids:
                            variant.create_product_changes('DELETE',description)
                    elif vals['available_in_pos']:
                        for variant in record.product_variant_ids:
                            variant.create_product_changes('UPDATE',description)
                elif record.sale_ok and record.available_in_pos:
                    for variant in record.product_variant_ids:
                        variant.create_product_changes('UPDATE',description)
        return res
