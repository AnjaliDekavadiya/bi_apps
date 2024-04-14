from odoo import fields, models

class WhatsAppScheduleDate(models.TransientModel):
    _name = "whatsapp.schedule.date"

    schedule_date = fields.Datetime(string='Scheduled for')
    message_id = fields.Many2one('whatsapp.message', required=True)

    def action_schedule_date(self):
        self.message_id.write({'state': 'scheduled', 'scheduled_date': self.schedule_date, "sending_date": self.schedule_date})
        self.message_id.send_message_action()
