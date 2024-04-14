# -*- coding: utf-8 -*-
#################################################################################
#    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import fields, api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    zoho_doc_number = fields.Char(string='Zoho Doc Number') 
