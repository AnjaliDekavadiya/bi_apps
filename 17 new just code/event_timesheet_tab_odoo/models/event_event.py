from odoo import fields, models

class Event(models.Model):
    _inherit = 'event.event'

    custom_timesheet_id = fields.One2many('account.analytic.line', 
        'custom_event_id',
        string='Timesheets' ,
        copy=False, 
        )
