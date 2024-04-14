from odoo import fields, models,api
import logging

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model
    def _action_done(self, feedback=False, attachment_ids=None):
        activity_type = self.activity_type_id.name
        cxt=self.env.context
        if self and cxt.get('type')!='import':
            mapping = self.env['hubspot.activity.mapping'].search([('odoo_id','=',self.id)])
            channels = self.env['channel.connection'].search([('connected','=',True)])
            if mapping:
                for channel in channels:
                    channel.update_activities(mapping.hubspot_id, activity_type)
        messages, next_activities = super(MailActivity, self)._action_done(feedback=feedback, attachment_ids=attachment_ids)
        return messages, next_activities
