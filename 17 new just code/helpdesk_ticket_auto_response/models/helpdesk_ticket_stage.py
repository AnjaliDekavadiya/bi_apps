# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class HelpdeskStageConfig(models.Model):
    _inherit = "helpdesk.stage.config"
    
    is_auto_response = fields.Boolean(
        string="Need Auto Response",
        copy=True,
    )
    # to_customer = fields.Boolean(
    #     string="Send to Customer?",
    #     copy=True,
    # )
    # document_follower = fields.Boolean(
    #     string="Send to Followers?",
    #     copy=True,
    # )
    # internal_users = fields.Boolean(
    #     string="Send to Users ?",
    #     copy=True,
    # )
    custom_tempalte_id = fields.Many2one(
        'mail.template',
        string="Response Email Template",
        copy=True,
        domain=[('model', '=', 'helpdesk.support')],
    )
    # internal_user_ids = fields.Many2many(
    #     'res.users',
    #     string="Internal Users",
    #     copy=True,
    # )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
