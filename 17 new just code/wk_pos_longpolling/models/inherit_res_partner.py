# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models
import json
import base64
from odoo.tools import date_utils
import logging
_logger = logging.getLogger(__name__)

from datetime import datetime



class ResPartner(models.Model):
    _inherit = "res.partner"

    def get_pos_fields(self):
        session = self.env['pos.session']
        result = session._loader_params_res_partner()
        return result['search_params']['fields']
        
    def write(self, vals):
        res = super(ResPartner,self).write(vals)
        vals_keys = set(vals.keys())
        description = ','.join(vals_keys)
        fields = set(self.get_pos_fields())
        common_fields = fields.intersection(vals_keys)
        if len(common_fields):
            for rec in self:
                partner_operations = self.env['pos.common.changes'].search([('model_name','=',"res.partner"),('record_id','=',rec.id),('state','in',['error','draft'])],order="id desc")
                if not len(partner_operations):
                    self.env['pos.common.changes'].create({
                        'record_id': rec.id,
                        'record': json.dumps(rec.read(self.get_pos_fields()), default=date_utils.json_default),
                        'operation': 'UPDATE',
                        'model_name': "res.partner",
                        'description': description,
                        'state':'draft'
                    })
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(ResPartner,self).create(vals)
        for each_res in res:
            if each_res:
                self.env['pos.common.changes'].create({
                    'record_id': each_res.id,
                    'record': json.dumps(each_res.read(self.get_pos_fields()), default=date_utils.json_default),
                    'operation': 'CREATE',
                    'model_name': "res.partner",
                    'description': 'New Partner Created',
                    'state':'draft'
                })
        return res


    def unlink(self):
        for rec in self:
            self.env['pos.common.changes'].create({
                'record_id': rec.id,
                'record': json.dumps(rec.read(self.get_pos_fields()), default=date_utils.json_default),
                'operation': 'DELETE',
                'model_name': "res.partner",
                'description': 'Partner Deleted',
                'state':'draft'
            })
        return super(ResPartner,self).unlink()
