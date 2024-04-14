# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountMove(models.Model):
    # _inherit = 'account.invoice' #odoo13
    _inherit = 'account.move'
    
    sale_user_group_id = fields.Many2one(
        'sale.user.group',
        string='Sales Group',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
