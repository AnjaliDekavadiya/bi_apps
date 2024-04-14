# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import json
import base64
from odoo.tools import date_utils
import logging
_logger = logging.getLogger(__name__)

from datetime import datetime



class AccountTax(models.Model):
    _inherit = "account.tax"

    def get_pos_fields(self):
        return ['name','amount', 'price_include', 'include_base_amount', 'is_base_affected', 'amount_type', 'children_tax_ids']
        
    def write(self, vals):
        res = super(AccountTax,self).write(vals)
        vals_keys = set(vals.keys())
        description = ','.join(vals_keys)
        fields = set(self.get_pos_fields())
        common_fields = fields.intersection(vals_keys)
        if len(common_fields):
            for rec in self:
                partner_operations = self.env['pos.common.changes'].search([('model_name','=',"account.tax"),('record_id','=',rec.id),('state','in',['error','draft'])],order="id desc")
                if not len(partner_operations):
                    self.env['pos.common.changes'].create({
                        'record_id': rec.id,
                        'record': json.dumps(rec.read(self.get_pos_fields()), default=date_utils.json_default),
                        'real_tax_amount': rec.amount,
                        'operation': 'UPDATE',
                        'model_name': "account.tax",
                        'description': description,
                        'state':'draft'
                    })
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(AccountTax,self).create(vals)
        if res:
            self.env['pos.common.changes'].create({
                'record_id': res.id,
                'record': json.dumps(res.read(self.get_pos_fields()), default=date_utils.json_default),
                'real_tax_amount': res.amount,
                'operation': 'CREATE',
                'model_name': "account.tax",
                'description': 'New tax Created',
                'state':'draft'
            })
        return res


    def unlink(self):
        for rec in self:
            self.env['pos.common.changes'].create({
                'record_id': rec.id,
                'record': json.dumps(rec.read(self.get_pos_fields()), default=date_utils.json_default),
                'operation': 'DELETE',
                'model_name': "account.tax",
                'description': 'Tax Deleted',
                'state':'draft'
            })
        return super(AccountTax,self).unlink()
