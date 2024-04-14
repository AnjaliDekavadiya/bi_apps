# -*- coding: utf-8 -*-

from odoo import models, fields

class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'
    
    occational_agent_ids = fields.Many2many(
        'res.users',
        'occational_res_user', #odoo13
        string='Occational Agents',
    )
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
