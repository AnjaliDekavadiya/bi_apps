# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AppointmentSlot(models.Model):
    # _name = 'appointment.slot'
    _name = 'appointment.slot.custom'
    _rec_name = 'day'
    _description = "Appointment Slot"
    
    @api.model
    def _get_week_days(self):
        return [
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday')
        ]
    
    day = fields.Selection(
        selection=_get_week_days,
        default='Monday',
        string="Day's",
        required = True,
    )
    slot_line_ids = fields.One2many(
        'appointment.slot.line',
        'slot_id',
        string="Appointment Line",
    )
    
    @api.constrains('day')
    def _day_validation(self):
        for days in self:
            day_ids = self.search_count([('day', '=', days.day)])
            if day_ids > 1:
                raise ValidationError(_('You can not set multiple Day with Days!'))

class AppointmentSlotLine(models.Model):
    _name = 'appointment.slot.line'
    _description = "Appointment Slot Line"
    
    time = fields.Char(
        string = 'Time',
    )
    slot_id = fields.Many2one(
        # 'appointment.slot',
        'appointment.slot.custom',
    )