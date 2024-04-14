# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models,api,_
from odoo.exceptions import ValidationError

class courier_stages(models.Model):
    _name = 'dev.courier.stages'
    _description = 'Courier Stages'
    _order = "sequence, name, id"

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10, help="Used to order stages. Lower is better.")
    fold = fields.Boolean('Fold in Kanban')
    allow_create_invoice = fields.Boolean('Allow Create Invoice')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
