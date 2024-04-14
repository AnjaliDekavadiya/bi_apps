# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):
        
    def _get_shop_payment_values(self, order, **kwargs):
        values = super(WebsiteSale, self)._get_shop_payment_values(order, **kwargs)
        # acq_list = values.get("acquirers", False)
        # acq_list = values.get("providers", False) #odoo16
        acq_list = values.get("providers_sudo", False) #odoo17
        res_partner = request.env.user.partner_id
        res_acq_list = list(res_partner.custom_payment_acquirer_ids)
        for ele in res_acq_list: 
            if acq_list and ele in acq_list: 
                acq_list -= ele#15
#                acq_list.pop(acq_list.index(ele))
        # odoo17
        payment_methods_sudo = request.env['payment.method'].sudo()._get_compatible_payment_methods(
            acq_list.ids,
            values.get('partner_id'),
            currency_id=values.get('currency').id,
        )
        values.update({
#            'acquirers': acq_list
            # 'providers': acq_list #odoo16
            'providers_sudo': acq_list, #odoo17
            'payment_methods_sudo': payment_methods_sudo,#odoo17
        })#15
        return values
     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
