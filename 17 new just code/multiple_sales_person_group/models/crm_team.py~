# -*- coding: utf-8 -*-

from odoo import models, fields

class Team(models.Model):
    _inherit = 'crm.team'
    
    sale_user_group_id = fields.Many2many(
        'sale.user.group',
        string='Sales Group',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
