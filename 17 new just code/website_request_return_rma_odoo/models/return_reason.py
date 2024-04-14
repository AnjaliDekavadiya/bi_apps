# -*- coding: utf-8 -*-

from odoo import fields, models


class ReturnReason(models.Model):
    _name = 'return.reason'
    _description = "Return Reason"
   
    name = fields.Char(
        string='Name',
        required = True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
