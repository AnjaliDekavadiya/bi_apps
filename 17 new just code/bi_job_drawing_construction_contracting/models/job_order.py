# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

SCOPES = 'https://www.googleapis.com/auth/drive'


class GoogleContractdrawing(models.Model):
    _name = 'google.contract.drawings'
    _description = 'Google image'

    name = fields.Char(string='Drawing Name')
    description = fields.Char(string='Description')
    drawing_url = fields.Char(string="Drawing Url")
    job_order_id = fields.Many2one('job.order', 'Job Order')

    def attachment_contract_img_button(self):
        return {
            'name': 'Go to google drive',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': self.drawing_url,
        }


class JobOorder(models.Model):
    _inherit = "job.order"

    google_contract_drawings_ids = fields.One2many('google.contract.drawings', 'job_order_id',
                                                   string='Contract Drawings')

    def create_google_drawing(self):
        return {
            'name': 'Go to google drive',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://docs.google.com/drawings/create',
        }
