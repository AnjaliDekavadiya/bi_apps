from lxml import etree

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(MailThread, self).get_view(view_id=view_id, view_type=view_type, **options)

        if view_type == 'calendar' and options.get('action_id') == self.env.ref('calendar_resource_assignee_mac5.action_calendar_event_by_assignee').id:
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//calendar"):
                node.set('resource_by_assignee', 'resource_by_assignee')
                node.set('resource_type', 'timegrid')
            result['arch'] = etree.tostring(doc)
        return result
