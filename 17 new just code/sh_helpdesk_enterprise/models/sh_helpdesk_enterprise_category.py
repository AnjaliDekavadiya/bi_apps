# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class HelpdeskCategory(models.Model):
    _name = 'sh.helpdesk.category'
    _description = 'Helpdesk Category'
    _rec_name = 'name'

    sequence = fields.Integer(string="Sequence")
    name = fields.Char(required=True, string='Name', translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        for value in vals_list:
            sequence = self.env['ir.sequence'].next_by_code('helpdesk.category')
            value['sequence'] = sequence
        return super(HelpdeskCategory, self).create(vals_list)
