from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    is_meeting_assignee = fields.Boolean(string="Is meeting assignee?")
    meeting_assignee_sequence = fields.Integer(default=16)
