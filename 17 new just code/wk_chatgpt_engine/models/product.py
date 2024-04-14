# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields
from odoo.tools import html2plaintext
from odoo.exceptions import UserError
from odoo.tools import split_every


import logging

_logger = logging.getLogger(__name__)



class ProductTemplate(models.Model):
    _inherit = "product.template"
    


    def suggest_seo_wizard(self):
        ctx = {'product': self.id, 'model_active': self._name}
        wizard_id = self.env.ref('wk_chatgpt_engine.suggest_seo_wizard_form').id
        return {
            'name': 'Suggest SEO Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(wizard_id, 'form')],
            'res_model': 'suggest.seo.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }
    
        
        
class ProductCategory(models.Model):
    _inherit = "product.public.category"
    


    def suggest_seo_wizard(self):
        ctx = {'product': self.id, 'model_active': self._name}
        wizard_id = self.env.ref('wk_chatgpt_engine.suggest_seo_wizard_form').id
        return {
            'name': 'Suggest SEO Wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(wizard_id, 'form')],
            'res_model': 'suggest.seo.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }