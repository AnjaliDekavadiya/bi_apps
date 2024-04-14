# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionLevel(models.Model):
    _inherit = 'sale.commission.level'

    web_shop_agent_level = fields.Boolean(
        string="Use Webshop Sales Agent"
    )
    web_shop_sales_person_level = fields.Boolean(
        string="Use Webshop Sales Person",
    )

    @api.constrains('web_shop_agent_level', 'web_shop_sales_person_level')
    def _validate_web_shop_agent(self):
        for rec in self:
            if rec.web_shop_agent_level:
                web_shop_agent_level_ids = self.env['sale.commission.level'].search([('web_shop_agent_level', '=', True), ('id', '!=', rec.id)])
                if web_shop_agent_level_ids:
                    raise ValidationError("Webshop Sales Agent Level should not be more than one")
            if rec.web_shop_sales_person_level:
                web_shop_sales_person_level_ids = self.env['sale.commission.level'].search([('web_shop_sales_person_level', '=', True), ('id', '!=', rec.id)])
                if web_shop_sales_person_level_ids:
                    raise ValidationError("Webshop Sales Person Level should not be more than one")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
