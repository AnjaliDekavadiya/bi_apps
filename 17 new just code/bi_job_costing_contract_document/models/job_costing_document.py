# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class InheritDirectory(models.Model):
    _inherit = "directorie.document"

    job_document_id = fields.Many2one("job.costing.document", string="Job Document")


class JobCostDocument(models.Model):
    _name = "job.costing.document"

    directory_ids = fields.One2many("directorie.document", 'job_document_id', string="Directory Document")


class InheritJobCostSheet(models.Model):
    _inherit = "job.cost.sheet"

    def button_count_document(self):
        self.ensure_one()
        return {
            'name': 'Attachments',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'ir.attachment',
            'context': {'create': True},

        }

    document_count = fields.Integer(compute='_docum_count', string="Attachments")

    def _docum_count(self):
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id', 'res_model'])
        self.document_count = len(attachments)


class InheritOrder(models.Model):
    _inherit = "job.order"

    def butoon_order_document(self):
        self.ensure_one()
        return {
            'name': 'Attachments',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'ir.attachment',
            'context': {'create': True},
        }
