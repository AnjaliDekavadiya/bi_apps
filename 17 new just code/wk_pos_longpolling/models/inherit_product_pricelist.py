# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import models, fields, api, _
import json
import base64
from odoo.tools import date_utils
import logging
_logger = logging.getLogger(__name__)


class PricelistItemLongPoll(models.Model):
    _inherit = "product.pricelist.item"
    
   
    def write(self, vals):
        vals_keys = vals.keys()     
        change_vals = ','.join(vals_keys)  
        res = super(PricelistItemLongPoll,self).write(vals) 
        if len(vals_keys):
            for record in self:
                record.create_pricelist_changes(record.id, record, 'UPDATE',change_vals)
        return res

    def create_pricelist_changes(self,pl_item_id, record, operation,change_vals):
        price_operations = self.env['pos.common.changes'].search([('model_name','=',"product.pricelist.item"),('record_id','=', pl_item_id),('state','=','draft')],order="id desc")
        if not len(price_operations):
            data = record.read()
            if operation == 'UPDATE':
                self.env['pos.common.changes'].create({
                    'record_id': pl_item_id,
                    'record': json.dumps(data, default=date_utils.json_default),
                    'model_name': 'product.pricelist.item',
                    'operation': "UPDATE",
                    'state': "draft",
                    'description':change_vals
                })  
            else:
                self.env['pos.common.changes'].create({
                    'record_id': pl_item_id,
                    'record': json.dumps(data, default=date_utils.json_default),
                    'model_name': 'product.pricelist.item',
                    'operation': "DELETE",
                    'state': "draft",
                    'description':change_vals
                })

    @api.model_create_multi
    def create(self, vals):
        record = super(PricelistItemLongPoll,self).create(vals)
        self.env['pos.common.changes'].create({
            'record_id': record.id,
            'record': json.dumps(record.read(), default=date_utils.json_default),
            'model_name': 'product.pricelist.item',
            'operation': "CREATE",
            'state': "draft",
            'description':'New Pricelist Item Created'
        })
        return record

    def unlink(self):
        for record in self:
            record.create_pricelist_changes(record.id, record, 'DELETE','Pricelist Item Deleted')
        return super(PricelistItemLongPoll,self).unlink()