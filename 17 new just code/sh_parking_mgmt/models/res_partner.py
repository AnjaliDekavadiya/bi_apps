# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sh_is_memeber = fields.Boolean(string="is Member")
