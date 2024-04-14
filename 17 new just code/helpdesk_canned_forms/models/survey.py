# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Survey(models.Model):
    _inherit = "survey.survey"
    
    ticket_partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
