'''
Created on Oct 27, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class ContractType(models.Model):
    _inherit = 'hr.contract.type'
    _order = 'sequence, id'

    code = fields.Char(required=True)
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    active = fields.Boolean(default = True)