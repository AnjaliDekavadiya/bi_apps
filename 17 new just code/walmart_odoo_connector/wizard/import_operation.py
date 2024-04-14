# -*- coding: utf-8 -*-
##########################################################################
#
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################
from odoo import models, fields, api, _
from odoo.addons.odoo_multi_channel_sale.ApiTransaction import Transaction

class ImportOperation(models.TransientModel):
    _inherit = 'import.operation'

    walmart_default_import_button_hide = fields.Boolean()
    walmart_filter_type = fields.Selection(
        selection=[
            ('all', 'All'),
            ('date_range', 'Date Range'),
            ('id', 'By ID/SKU'),
        ],
        default='all',
        required=True,
    )
    walmart_object_id = fields.Char()
    walmart_created_at_min = fields.Datetime()
    walmart_created_at_max = fields.Datetime()

    @api.onchange('channel_id')
    def _onchange_channel_id(self):
        if self.channel == 'walmart':
            self.walmart_default_import_button_hide = True
        else:
            self.walmart_default_import_button_hide = False

    def import_button(self):
        kw = {'object':self.object}
        kw.update(self.walmart_get_filter())
        return self.import_with_filter(**kw)

    def walmart_get_filter(self):
        kw = {'filter_type': self.walmart_filter_type}
        if self.walmart_filter_type == 'id':
            kw['object_id'] = self.walmart_object_id
        elif self.walmart_filter_type == 'date_range':
            kw['created_at_min'] = self.walmart_created_at_min.replace(microsecond=0).isoformat()
            if self.walmart_created_at_max:
                kw['created_at_max'] = self.walmart_created_at_max.replace(microsecond=0).isoformat()
        return kw

    def walmart_back_button(self):

        return {'name': "Import Operation",
                'view_mode': 'form',
                'view_id': False,
                'res_model': self._name,
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                }

    def walmart_next_button(self):
        # cntx = self._context.copy() or {}
        rec = self.env['walmart.import.operation'].create({'channel_id': self.channel_id.id})
        domain = [('ecom_store', '=', 'walmart'), ('leaf_category', '=',
                                                False), ('channel_id', '=', self.channel_id.id)]

        ids = self.env["channel.category.mappings"].search(domain).ids
        return {
            'name': _('Walmart Category Import'),
            'view_mode': 'form',
            'res_model': 'walmart.import.operation',
            'context': {'_walmart_category_ids':ids},
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': rec.id,
        }


class WalmartImportOperation(models.TransientModel):
    _name = 'walmart.import.operation'
    _description = 'Walmart Import Operation'

    object = fields.Selection(selection=[
            ('product.category', 'Category'),
        ],
        default='product.category',
    )
    operation = fields.Selection(
        selection = [
            ('import',"Import"),
            ('update','Update')
        ],
        default ='import',
        required = True
    )
    channel_id=fields.Many2one(
        comodel_name='multi.channel.sale',
        string      ='Channel ID',
        required    =True,
        domain      =[('state','=','validate')]
    )
    channel = fields.Selection(related='channel_id.channel')
    walmart_category_ids = fields.Many2many(
        relation='walmart_import_category_rel',
        comodel_name='channel.category.mappings',
        string='Walmart Category',
    )

    def import_button(self):
        kw = {
            'object': self.object,
            'walmart_category_ids': self.walmart_category_ids,
        }
        return Transaction(channel=self.channel_id).import_data(**kw)

    def operation_back(self):
        ctx = dict(self._context or {})
        active_model = ctx.get('active_model')
        partial = self.env[active_model].browse(ctx.get('active_id'))
        partial.object = False
        ctx['active_id'] = False
        ctx['default_channel_id'] = False

        return {'name': "Import Operation",
                'view_mode': 'form',
                'view_id': False,
                'res_model': active_model,
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx,
                }