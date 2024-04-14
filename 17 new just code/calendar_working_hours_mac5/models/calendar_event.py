from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.constrains('allday', 'start', 'stop')
    def _check_working_hours(self):
        company = self.env.user.company_id
        if company.calendar_schedule_id and company.calendar_schedule_backend_check:
            for event in self:
                if not event.allday and event.start and event.stop:
                    start = fields.Datetime.from_string(event.start)
                    stop = fields.Datetime.from_string(event.stop)
                    meeting_hours = (stop - start).total_seconds() / 3600
                    work_hours = company.calendar_schedule_id.get_work_hours_count(start, stop)
                    print(111, start, stop, meeting_hours, work_hours)
                    if meeting_hours != work_hours:
                        raise UserError(_("Meeting should be within working hours !"))
