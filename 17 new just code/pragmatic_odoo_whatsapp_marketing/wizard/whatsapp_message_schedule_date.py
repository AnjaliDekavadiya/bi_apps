# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WhatsappMessageScheduleDate(models.TransientModel):
    _name = 'whatsapp.message.schedule.date'
    _description = 'Whatsapp Message Scheduling'

    schedule_date = fields.Datetime(string='Scheduled for')
    whatsapp_message_id = fields.Many2one('whatsapp.marketing', "Whatsapp Message Id", ondelete='cascade')

    @api.constrains('schedule_date')
    def _check_schedule_date(self):
        for scheduler in self:
            if scheduler.schedule_date < fields.Datetime.now():
                raise ValidationError(_('Please select a date equal/or greater than the current date.'))

    def set_schedule_date(self):
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        self.write({'whatsapp_message_id': rec.id})
        self.whatsapp_message_id.write({'schedule_date': self.schedule_date, 'state': 'in_queue'})
