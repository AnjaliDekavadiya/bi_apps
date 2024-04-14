# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
from odoo.tools.misc import formatLang
from odoo import api,fields, models
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError


class website(models.Model):
    _inherit='website'
    
    def _get_loyalty_points(self ,product_variant_id,add_qty):
        self.clear_caches()
        data={}
        obj=self.env['sale.order'].sudo()._get_default_wk_loyalty_program_id()
        loyalty_base_config =  self.env['website.loyalty.management'].browse(int(obj))
        loyalty_base= loyalty_base_config.loyalty_base
        if obj and loyalty_base :
            
            if loyalty_base == "purchase":
                return False
            elif loyalty_base == "product":
                points=product_variant_id.product_tmpl_id.loyalty_benefit
                total= points*add_qty
            elif loyalty_base == "variant":
                points= product_variant_id.loyalty_benefit
                total= points*add_qty
                data.update({'total':total,'message':loyalty_base_config.loyalty_message})
                return data
            elif loyalty_base == "category":
                points= product_variant_id.categ_id.loyalty_benefit
                total= points*add_qty
            data.update({'total':total,'message':loyalty_base_config.loyalty_message})
            return data
        else:
            return False      
            
        

class Product(models.Model):
    _inherit = "product.template"
    loyalty_benefit = fields.Float(string="Loyalty Benefit")

    @api.constrains('loyalty_benefit')
    def _loyality_validation(self):
        for rec in self:
            if rec.loyalty_benefit :
                if rec.loyalty_benefit < 0 :
                    raise ValidationError("Loyalty Benefit points should be positive")

class ProductVariant(models.Model):
    _inherit = "product.product"
    loyalty_benefit = fields.Float(string="Loyalty Benefit")

    @api.constrains('loyalty_benefit')
    def _loyality_validation(self):
        for rec in self:
            if rec.loyalty_benefit :
                if rec.loyalty_benefit < 0 :
                    raise ValidationError("Loyalty Benefit points should be positive")

class ProductCategory(models.Model):
    _inherit = "product.category"
    loyalty_benefit = fields.Float(string="Loyalty Benefit")

    @api.constrains('loyalty_benefit')
    def _loyality_validation(self):
        for rec in self:
            if rec.loyalty_benefit :
                if rec.loyalty_benefit < 0 :
                    raise ValidationError("Loyalty Benefit points should be positive")
                

class AccountTax(models.Model):
        _inherit = 'account.tax'

        @api.model
        def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
            """
            Prepare tax totals and include loyalty points data if the base line corresponds to a sale order line.

            :param base_lines: List of base lines.
            :param currency: Currency information.
            :param tax_lines: Tax lines information.
            :return: A dictionary containing tax totals with loyalty points data if applicable.
            """
            res = super()._prepare_tax_totals(base_lines, currency, tax_lines)
            if base_lines and base_lines[0]['record']._name == "sale.order.line":
                order_id = base_lines[0]['record'].order_id
                loyalty_data = {}
                if order_id.wk_extra_loyalty_points:
                    loyalty_data.update({'wk_extra_loyalty_points': order_id.wk_extra_loyalty_points})
                if order_id.wk_website_loyalty_points:
                    loyalty_data.update({'wk_website_loyalty_points': order_id.wk_website_loyalty_points, 'loyalty_state':order_id.wk_loyalty_state})
                if order_id.wk_extra_loyalty_points:
                    res.update({'formatted_amount_total': formatLang(self.env, res.get('amount_total'), currency_obj=currency) })    
                return {**res, **loyalty_data}
            return res