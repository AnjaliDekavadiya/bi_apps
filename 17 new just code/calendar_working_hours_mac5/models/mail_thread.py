import json
from lxml import etree

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(MailThread, self).get_view(view_id=view_id, view_type=view_type, **options)

        company = self.env.user.company_id
        if view_type == 'calendar':
            company_data = {}

            if company.calendar_schedule_id:
                # Get working hours
                schedules = [{
                    'daysOfWeek': [(int(a.dayofweek) + 1) % 7],
                    'startTime': '{0:02.0f}:{1:02.0f}'.format(*divmod(float(a.hour_from) * 60, 60)),
                    'endTime': '{0:02.0f}:{1:02.0f}'.format(*divmod(float(a.hour_to) * 60, 60)),
                } for a in company.calendar_schedule_id.attendance_ids if a.day_period != 'lunch']

                company_data.update({
                    'businessHours': schedules,
                    'calendarEventOnly': company.calendar_schedule_event_only,
                    'eventConstraint': company.calendar_schedule_event_check,
                    'selectConstraint': company.calendar_schedule_select_check,
                })

            doc = etree.XML(result['arch'])
            for node in doc.xpath("//calendar"):
                node.set('company_wh_data', json.dumps(company_data))
            result['arch'] = etree.tostring(doc)
        return result
