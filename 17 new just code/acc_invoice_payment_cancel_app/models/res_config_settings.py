# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    invoice_opration_type = fields.Selection(string='Invoice Opration Type', related="company_id.invoice_opration_type" ,readonly=False)
    payment_opration_type = fields.Selection(related="company_id.payment_opration_type" ,readonly=False)