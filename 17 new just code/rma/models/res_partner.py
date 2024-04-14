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
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    count_rma = fields.Integer(
        string='count rma',
        compute='_compute_count_rma' 
    )
        
    @api.depends('count_rma')
    def _compute_count_rma(self):
        for record in self:
            record.count_rma = self.env['rma.rma'].sudo().search_count([('partner_id', '=', record.id)])
    
    def get_customer_rma(self):
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'list,form',
            'view_mode': 'list,form',
            'res_model': 'rma.rma',
            'domain': [('partner_id', '=', self.id)],
        }
    