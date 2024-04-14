# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import datetime
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_lines_with_or_without_delivery(self):
        """This method used on payment page. Return [{lines, deliveries, store_ids}]]"""
        self.ensure_one()
        del_lines = []
        sol_lines = super(SaleOrder, self).get_lines_with_or_without_delivery()
        store_delivery = self.env["delivery.carrier"].search([('website_published','=',True),('is_store_carrier','=',True)],limit=1)
        if not store_delivery:
            return sol_lines
        for sol in sol_lines:
            if sol.get('type') and sol['type'] == 'service':
                del_lines.append(sol)
                continue
            lines = sol.get('lines')
            mp_lines = lines.filtered(lambda l: l.marketplace_seller_id)
            if mp_lines:
                data = {}
                store_lines = self.env["sale.order.line"]
                for line in mp_lines:
                    store_ids = line.product_id.product_tmpl_id.seller_shop_ids.filtered(lambda s: s.store_lat and s.store_long and s.website_published and s.available_for_pickup)
                    if store_ids:
                        store_lines += line
                        del_key = "/".join(map(str, store_ids.ids))
                        if data.get(del_key):
                            data[del_key]['lines'] += line
                        else:
                            data[del_key] = {'lines': line, 'store_ids': store_ids}
                if store_lines:
                    without_store_lines = lines - store_lines
                    if without_store_lines:
                        del_lines.append({
                            'lines': without_store_lines,
                            'deliveries': sol.get('deliveries'),
                            'type': 'non_service',
                        })
                else:
                    del_lines.append(sol)

                for store_line in data.values():
                    del_lines.append({
                        'lines': store_line['lines'],
                        'deliveries': sol['deliveries'] + store_delivery,
                        'type': 'non_service',
                        'store_ids': store_line['store_ids']
                    })
            else:
                del_lines.append(sol)
        return del_lines

    def _get_delivery_methods(self):
        methods = super(SaleOrder, self)._get_delivery_methods()
        return methods.filtered(lambda m: not m.is_store_carrier)

class SaleOderLine(models.Model):
    _inherit = "sale.order.line"

    store_id = fields.Many2one("seller.shop","PickUp Store")
    is_store_pickup = fields.Boolean("Store Pickup")
    store_address = fields.Char("PickUp Address", related="store_id.contact_address")
    pickup_date = fields.Date("Pick Up Date")
    pickup_time = fields.Char("Pick Up Timing")

    def set_store_pickup(self, **kw):
        store_id = kw.get('store_id', False)
        pickup_time = kw.get('pickup_time', False)
        pickup_date = kw.get('pickup_date', False)
        lines = self.filtered(lambda l: l.state == 'draft')
        if lines and store_id:
            store_obj = self.env["seller.shop"].browse(int(store_id))
            data = {
                'is_store_pickup' : True,
                'store_id' : store_obj.id,
            }
            if pickup_date:
                pickup_date = datetime.datetime.strptime(pickup_date, '%m/%d/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                data['pickup_date'] = pickup_date
            if pickup_time:
                data['pickup_time'] = pickup_time
            lines.update(data)  
      
        return True


    def remove_store_pickup(self):
        for rec in self:
            if rec.state == 'draft':
                rec.is_store_pickup = False
                rec.store_id = False
                rec.store_address = False
                rec.pickup_date = False
                rec.pickup_time = False
        return True

    def get_delivery_carrier_ids(self):
        self.ensure_one()
        deliveries = super(SaleOderLine,self).get_delivery_carrier_ids()
        # Need to check the address configured in store delivery. available_carriers(address)
        store_delivery = self.env["delivery.carrier"].search([('website_published','=',True),('is_store_carrier','=',True)],limit=1)
        if store_delivery:
            product_store_ids = self.product_id.product_tmpl_id.seller_shop_ids.filtered(lambda s: s.store_lat and s.store_long and s.website_published)
            if product_store_ids:
                if not deliveries:
                    deliveries = self.order_id._get_delivery_methods()
                deliveries = deliveries | store_delivery
                return deliveries
        return deliveries
