# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)
class WebkulWebsiteAddons(models.TransientModel):
    _inherit = 'res.config.settings'

    module_odoo_age_verification = fields.Boolean(string="Odoo Age Verification")

    def get_age_configuration_view(self):
        ageConfigObjs = self.env['age.verification.config.settings'].search([])
        imd = self.env['ir.model.data']
        res_model, res_id = imd._xmlid_to_res_model_res_id('odoo_age_verification.action_age_config_view')
        if res_model and res_id:
            actionObj = self.env[res_model].browse(res_id)
            treeId = imd._xmlid_to_res_id('odoo_age_verification.age_config_tree_view')
            formId = imd._xmlid_to_res_id('odoo_age_verification.age_config_view')

            result = {
                'name': actionObj.name,
                'help': actionObj.help,
                'type': actionObj.type,
                'views': [[treeId, 'tree'],[formId, 'form']],
                'target': actionObj.target,
                'context': actionObj.context,
                'res_model': actionObj.res_model,
            }
            if len(ageConfigObjs) == 1:
                result['views'] = [(formId, 'form')]
                result['res_id'] = ageConfigObjs[0].id
            return result