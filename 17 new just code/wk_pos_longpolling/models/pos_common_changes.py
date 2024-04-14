# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from datetime import datetime, timedelta
from odoo import models, fields, api, _
import logging
import json
import base64
from odoo.tools import date_utils

_logger = logging.getLogger(__name__)



class PosCommonChanges(models.Model):
    _name = 'pos.common.changes'
    _description = "Pos Common Changes"
    
    
   
    model_name = fields.Char('Model Name')
    record_id = fields.Integer('Record Id')
    record = fields.Text('Modified Record')
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('done', 'Done'), ('failed', 'Failed')],
        default='draft'
    )
    real_tax_amount = fields.Float("Real Tax Amount")
    operation = fields.Selection(
        selection=[('DELETE', 'DELETE'), ('UPDATE', 'UPDATE'), ('CREATE', 'CREATE')])
    description = fields.Text(string="Description")
    
    
    @api.model_create_multi
    def create(self, vals):
        res = super(PosCommonChanges, self).create(vals)
        try:
           self.get_pos_common_changes()
        except Exception as e:
            _logger.info("****************Exception***********:%r", e)
        return res
    
    @api.model
    def remove_extra_changes(self):
        records = self.sudo().search([('state', '=', 'done')])
        if len(records):
            records.unlink()

    @api.model
    def get_pos_common_changes(self):
        records = self.sudo().search([('state', '!=', 'done')])
        if records:
            self._notify_changes_in_pos(records)
            records.update({
            'state': 'done'
        })
        return records
    
    def get_formatted_channel_name(self, db_name, config_id, channel='wk_pos_longpolling'):
        return '{}_{}_{}'.format(db_name, channel, config_id)
        
    
    def _notify_changes_in_pos(self, records):
        """ Sends through the bus the changes of given partners in the pos"""
        notifications = []
        data = [{'operation': rec.operation, 'model_name': rec.model_name, 'record_id': rec.record_id, 'record': json.loads(rec.record), 'amount': rec.real_tax_amount} for rec in records]
        try:
            if data[0]['model_name'] == 'product.pricelist.item':
                item = data[0]
                if item['record'][0]['product_id']:
                    product_data = self.env['product.template'].browse(item['record'][0]['product_id'][0])
                    product_data.create_product_changes('UPDATE', 'lst_price')
                else:
                    template_id = self.env['product.template'].browse(item['record'][0]['product_tmpl_id'][0])
                    for variant in template_id.product_variant_ids:
                        variant.create_product_changes('UPDATE', 'lst_price')
        except:
            pass
            
        for config_id in self.get_active_session_ids():
            channel = self.get_formatted_channel_name(self.env.cr.dbname, config_id)
            notifications.append([channel, "pos_data_update", data])
        if len(notifications) > 0:
            self.env['bus.bus']._sendmany(notifications)
            
    def get_active_session_ids(self):
        sessions = self.env['pos.session'].search([('state', '!=', 'closed')])
        if len(sessions):
            return sessions.mapped('config_id').ids
    
    
    