# -*- coding: utf-8 -*-

from odoo import models, fields

class Partner(models.Model):
    _inherit = 'res.partner'
    
    sale_user_group_id = fields.Many2one(
        'sale.user.group',
        string='Sales Group',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
