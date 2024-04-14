# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection([
        ('3_global', 'All Products'),
        ('2_product_category', 'Product Category'),
        ('31_product_brand', 'Product Brand'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='3_global', required=True,
        help='Pricelist Item applicable on selected option')
    product_brand = fields.Many2one('product.brand.gcs', string='Product Brand')

    # New 4th Rule Fields
    categ_product_brand = fields.Many2one('product.brand.gcs', string='Product Brand')
    categ_brand_id = fields.Many2one('product.category', 'Product Category', ondelete='cascade',
                                     help="Specify a product category if this rule only applies to products belonging to this category or its \
            children categories. Keep empty otherwise.")

    # === COMPUTE METHODS ===#
    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge', 'categ_product_brand')
    def _compute_name_and_price(self):
        super(PricelistItem, self)._compute_name_and_price()
        for item in self:
            if item.categ_product_brand and item.applied_on == '31_product_brand':
                item.name = _("Brand: %s") % (item.categ_product_brand.name)

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('applied_on', False):
                # Ensure item consistency for later searches.
                applied_on = values['applied_on']
                if applied_on == '3_global':
                    values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None, product_brand=None,
                                       categ_product_brand=None, categ_brand_id=None))
                elif applied_on == '31_product_brand':
                    values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None, product_brand=None))
                elif applied_on == '2_product_category':
                    values.update(
                        dict(product_id=None, product_tmpl_id=None, categ_product_brand=None, categ_brand_id=None))
                elif applied_on == '1_product':
                    values.update(dict(product_id=None, categ_id=None, product_brand=None, categ_product_brand=None,
                                       categ_brand_id=None))
                elif applied_on == '0_product_variant':
                    values.update(
                        dict(categ_id=None, product_brand=None, categ_product_brand=None, categ_brand_id=None))
        return super(PricelistItem, self).create(vals_list)

    def write(self, values):
        if values.get('applied_on', False):
            # Ensure item consistency for later searches.
            applied_on = values['applied_on']
            if applied_on == '3_global':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None, product_brand=None,
                                   categ_product_brand=None, categ_brand_id=None))
            elif applied_on == '31_product_brand':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None, product_brand=None))
            elif applied_on == '2_product_category':
                values.update(
                    dict(product_id=None, product_tmpl_id=None, categ_product_brand=None, categ_brand_id=None))
            elif applied_on == '1_product':
                values.update(dict(product_id=None, categ_id=None, product_brand=None, categ_product_brand=None,
                                   categ_brand_id=None))
            elif applied_on == '0_product_variant':
                values.update(dict(categ_id=None, product_brand=None, categ_product_brand=None, categ_brand_id=None))
        res = super(PricelistItem, self).write(values)
        return res

    def _is_applicable_for(self, product, qty_in_product_uom):
        """Check whether the current rule is valid for the given product & qty.

        Note: self.ensure_one()

        :param product: product record (product.product/product.template)
        :param float qty_in_product_uom: quantity, expressed in product UoM
        :returns: Whether rules is valid or not
        :rtype: bool
        """
        print("Product is", product)
        self.ensure_one()
        product.ensure_one()
        res = True

        is_product_template = product._name == 'product.template'
        if self.min_quantity and qty_in_product_uom < self.min_quantity:
            res = False

        # Rule: 2_product_category
        elif self.categ_id and self.product_brand:
            # Applied on a specific category
            cat = product.categ_id
            product_brand1 = product.product_brand_gcs
            while cat:
                if cat.id == self.categ_id.id and product_brand1 == self.product_brand:
                    break
                cat = cat.parent_id
            if not cat:
                res = False
        elif self.categ_id and not self.product_brand:
            # Applied on a specific category
            cat = product.categ_id
            while cat:
                if cat.id == self.categ_id.id:
                    break
                cat = cat.parent_id
            if not cat:
                res = False

        # Rule: 31_product_brand
        # categ_product_brand: Product Brand 2
        # categ_brand_id: Category 2
        elif self.categ_product_brand and self.categ_brand_id:
            # Applied on a specific category
            cat = product.categ_id
            product_brand2 = product.product_brand_gcs
            while cat:
                if cat.id == self.categ_brand_id.id and product_brand2 == self.categ_product_brand:
                    break
                cat = cat.parent_id
            if not cat:
                res = False
        elif self.categ_product_brand and not self.categ_brand_id:
            product_brand2 = product.product_brand_gcs
            if product_brand2 != self.categ_product_brand:
                res = False
        else:
            # Applied on a specific product template/variant
            if is_product_template:
                if self.product_tmpl_id and product.id != self.product_tmpl_id.id:
                    res = False
                elif self.product_id and not (
                        product.product_variant_count == 1
                        and product.product_variant_id.id == self.product_id.id
                ):
                    # Product self acceptable on template if it has only one variant
                    res = False
            else:
                if self.product_tmpl_id and product.product_tmpl_id.id != self.product_tmpl_id.id:
                    res = False
                elif self.product_id and product.id != self.product_id.id:
                    res = False
        return res
