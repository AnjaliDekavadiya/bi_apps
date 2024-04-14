# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CreateMeetingLaundryCustom(models.TransientModel):
    _name = "create.meeting.laundry.custom"
    _description = 'Meeting Appointment'
    
    meeting_custom_type = fields.Selection(
        [('collection_type','Appointment for Collection'),
        ('delivery_type','Appointment for Delivery')],
        string='Appointment Type',
        required=True,
    )
    meeting_subject = fields.Char(
        string='Appointment Subject',
        required=True,
    )
    attendees_ids = fields.Many2many(
        'res.partner',
        string='Appointment Attendees',
        required=True,
    )
    start_date_time = fields.Datetime(
        string='Appointment Start Datetime',
        required=True,
    )
    stop_date = fields.Datetime(
        string='Appointment Stop Datetime',
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Collection / Delivery User',
        required=True
    )

    @api.onchange('meeting_custom_type')
    def onchange_appointmet_type(self):
        laundry_id = self._context.get('active_id')
        laundry_rec = self.env['laundry.business.service.custom'].browse(int(laundry_id))
        if self.meeting_custom_type == 'collection_type':
            self.user_id = laundry_rec.collection_user_id.id
        elif self.meeting_custom_type == 'delivery_type':
            self.user_id = laundry_rec.delivery_user_id

    @api.model
    def default_get(self, fields):
        res = super(CreateMeetingLaundryCustom, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'laundry.business.service.custom':
            record = self.env[model].browse(active_id)
            res.update({
                'attendees_ids': record.partner_id,
            })
        return res

    def create_meeting_custom(self):
        laundry_id = self._context.get('active_id')
        laundry_rec = self.env['laundry.business.service.custom'].browse(laundry_id)
        action = self.env.ref("laundry_meetings_appointments.custom_meeting_delivery_action").sudo().read()[0]
        action['context'] = {
            'default_name': self.meeting_subject,
            'default_meeting_custom_type': self.meeting_custom_type,
            'default_laundry_request_custom_id': laundry_rec.id,
            'default_partner_ids': self.attendees_ids.ids,
            'default_start': self.start_date_time,
            'default_stop': self.stop_date,
            'default_user_id': self.user_id.id,
        }
        return action