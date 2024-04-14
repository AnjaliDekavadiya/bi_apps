# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models

class PosSession(models.Model):

    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        res = super(PosSession, self)._loader_params_res_partner()
        res['search_params']['fields'].append('not_allow_partial_payment')
        return res
    
    def get_order_fields(self):
        return super().get_order_fields()+['pos_order.sh_amount_residual','pos_order.amount_paid']