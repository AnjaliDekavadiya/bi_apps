# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models , api


class Location(models.Model):

    _name = 'sh.parking.location'
    _description = 'Parking Location'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string='Location Name',required=True)
    parent_id = fields.Many2one(comodel_name="sh.parking.location",string="Parent Location", index=True, ondelete='cascade')
    complete_name = fields.Char(string='Complete Name', compute='_compute_complete_name', recursive=True,store=True)
    parent_path = fields.Char(index=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name
