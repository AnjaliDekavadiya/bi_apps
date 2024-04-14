# -*- coding: utf-8 -*-

from odoo import models


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False, update_pricelist=False):
        sale_order = super(Website, self).sale_get_order(force_create=force_create, update_pricelist=update_pricelist)
        if sale_order:
            sale_order._check_cash_on_deliver()
        return sale_order
