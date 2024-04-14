from odoo import fields, models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    custom_event_id = fields.Many2one('event.event', 
        string='Event' ,
        copy=False, 
        )