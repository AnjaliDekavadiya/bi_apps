# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleUserGroup(models.Model):
    _name = 'sale.user.group'
    _description = 'Sale User'
    
    name = fields.Char(
        string='Name',
        required =  True,
    )
    code = fields.Char(
        string='Code',
    )
    group_ids = fields.Many2many(
        'res.users',
        string='Sales Users',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
