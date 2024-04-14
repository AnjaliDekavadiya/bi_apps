# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'
    
    capture_attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Capture Photos',
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
