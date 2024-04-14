# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-Today Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Anil R. Kesariya(<http://www.jupical.com>)
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
from odoo import api, models, fields, _

class ProductProduct(models.Model):
    _inherit = "product.product"

    valuation = fields.Float("Valuation", compute="_get_valuation")
    
    def _get_valuation(self):
        for rec in self:
            total_cost = 0            
            for stock_lot in self.env['stock.production.lot'].search([('product_id', '=', rec.id)]):
                    total_cost += (stock_lot.price_unit * stock_lot.product_qty)
            rec.valuation = total_cost

    def action_real_cost_valuation(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("jt_prod_valuation.action_valuation_history")
        action['domain'] = [('product_id', '=', self.id)]
        action['context'] = {
            'default_product_tmpl_id': self.id,
            'default_company_id': (self.company_id or self.env.company).id,
        }
        if self.product_variant_count == 1:
            action['context'].update({
                'default_product_id': self.product_variant_id.id,
            })
        return action    