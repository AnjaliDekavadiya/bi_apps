# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LaundryStageCustom(models.Model):
    _name = 'laundry.stage.custom'
    _rec_name = 'name'
    _description = 'Laundry Stages'
    
    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        'Sequence',
        default=1,
        help="Used to order stages. Lower is better."
    )
    stage_type = fields.Selection(
        [('new','New'),
         ('collected','Collected'),
         ('tagging','Tagging'),
         ('marking','Marking'),
         ('assigned','Assigned'),
         ('watering','Watering'),
         ('washing','Washing'),
         ('drying','Drying'),
         ('folding','Folding'),
         ('pressing','Pressing'),
         ('reopened','Re Opened'),
         ('delivered','Delivered'),
         ('closed','Closed')],
        copy=False,
        string='Type',
    )
    fold = fields.Boolean(
        'Folded in Laundry',
        help='This stage is folded in the kanban view when there are no records in that stage to display.'
    )

    def unlink(self):
        if self.id:
            raise UserError(_('You can not laundry stage record.'))
        return super(LaundryStageCustom, self).unlink()