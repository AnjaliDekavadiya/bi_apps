# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
from odoo import fields, models, api
_logger = logging.getLogger(__name__)

EXTENDED_OPTIONS = [('product', 'Product Template'),('variant','Product variant')]

class WebsiteLoyaltyManagement(models.Model):
    _inherit = "website.loyalty.management"

    loyalty_base =fields.Selection(selection_add=EXTENDED_OPTIONS)
    loyalty_message= fields.Char(string ="Loyalty Message")

    @api.model
    def get_loyalty_points(self, amount, **kwargs):
    # Retrieve the loyalty_base from the current object instance
        loyalty_base = self.loyalty_base

        # Check if the loyalty_base is set to "purchase"
        if loyalty_base == "purchase":
            # If it is "purchase", use the base class's (super class) get_loyalty_points method
            return super().get_loyalty_points(amount, **kwargs)
        else:
            # If it is not "purchase", we need additional information about the order to calculate loyalty points

            # Retrieve the order_id from the keyword arguments
            order_id = kwargs.get('order_id')

            # Retrieve the order lines associated with the order_id
            order_line = order_id.order_line

            # Check different scenarios based on the loyalty_base value

            if loyalty_base == "category":
                # If loyalty_base is "category", calculate loyalty points based on category loyalty benefits
                return sum([line.product_id.categ_id.loyalty_benefit * line.product_uom_qty for line in order_line])
            elif loyalty_base == "product":
                # If loyalty_base is "product", calculate loyalty points based on product loyalty benefits
                return sum([line.product_id.product_tmpl_id.loyalty_benefit * line.product_uom_qty for line in order_line])
            elif loyalty_base == "variant":
                # If loyalty_base is "variant", calculate loyalty points based on variant loyalty benefits
                return sum([line.product_id.loyalty_benefit * line.product_uom_qty for line in order_line])
