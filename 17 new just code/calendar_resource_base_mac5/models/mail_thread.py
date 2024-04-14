from lxml import etree

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(MailThread, self).get_view(view_id=view_id, view_type=view_type, **options)

        if view_type == 'calendar':
            license = self.env['ir.config_parameter'].sudo().get_param('calendar_resource_base_mac5.fc_premium_license') or ''
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//calendar"):
                node.set('fc_premium_license', license)
            result['arch'] = etree.tostring(doc)
        return result
