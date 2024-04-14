# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    saas_service = fields.Boolean(string="SAAS Service", default=False, required=False, tracking=True)
    saas_package = fields.Many2many("dx.saas.packages", string="SAAS Package", tracking=True)
    saas_server = fields.Many2one("dx.saas.dbfilter.servers", string="SAAS Server", tracking=True)
    saas_users = fields.Integer(string="Users Number", required=False, default=1, tracking=True)
    saas_valid_for = fields.Integer(string="Valid for", required=True, default=1, tracking=True)
