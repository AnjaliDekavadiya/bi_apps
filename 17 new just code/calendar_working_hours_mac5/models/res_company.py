from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    calendar_schedule_id = fields.Many2one('resource.calendar', string="Working/Business Hours")
    calendar_schedule_event_only = fields.Boolean(string="Apply to Calendar Meetings Only",
                                                  default=True)
    calendar_schedule_event_check = fields.Boolean(string="Existing Meeting Restriction",
                                                   default=False)
    calendar_schedule_select_check = fields.Boolean(string="New Meeting Restriction",
                                                    default=False)
    calendar_schedule_backend_check = fields.Boolean(string="Meeting Backend Restriction",
                                                     default=False)
