from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    calendar_schedule_id = fields.Many2one(
        related='company_id.calendar_schedule_id',
        string='Working Hours', readonly=False
    )
    calendar_schedule_event_only = fields.Boolean(
        related='company_id.calendar_schedule_event_only',
        string='Apply to Calendar Meetings Only', readonly=False
    )
    calendar_schedule_event_check = fields.Boolean(
        related='company_id.calendar_schedule_event_check',
        string='Existing Meeting Restriction', readonly=False
    )
    calendar_schedule_select_check = fields.Boolean(
        related='company_id.calendar_schedule_select_check',
        string='New Meeting Restriction', readonly=False
    )
    calendar_schedule_backend_check = fields.Boolean(
        related='company_id.calendar_schedule_backend_check',
        string='Meeting Backend Restriction', readonly=False
    )
