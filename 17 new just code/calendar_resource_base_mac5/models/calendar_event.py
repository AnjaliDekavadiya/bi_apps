from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    assignee_user_id = fields.Many2one('res.users', string="Assignee", domain="[('is_meeting_assignee', '=', True)]")


class CalendarEventResourceTag(models.Model):
    _name = 'calendar.event.resource.tag'
    _description = "Meeting Resource Tags"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
