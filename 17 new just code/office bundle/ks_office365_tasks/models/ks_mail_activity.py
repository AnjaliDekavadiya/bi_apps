from odoo import fields, models, api
from odoo.addons.mail.models.mail_activity import MailActivity


class KsMailActivity(models.Model):
    _name = 'ks.mail.activity'

    @api.model
    def create(self, values):
        # already compute default values to be sure those are computed using the current user
        values_w_defaults = self.default_get(self._fields.keys())
        values_w_defaults.update(values)

        # continue as sudo because activities are somewhat protected
        activity = super(MailActivity, self.sudo()).create(values_w_defaults)
        # activity_user = activity.sudo(self.env.user)

        # send a notification to assigned user; in case of manually done activity also check
        # target has rights on document otherwise we prevent its creation. Automated activities
        # are checked since they are integrated into business flows that should not crash.
        if activity.user_id != self.env.user:
            if not activity.automated:
                activity._check_access_assignation()
            if not self.env.context.get('mail_activity_quick_update', False):
                activity.action_notify()

        # self.env[activity_user.res_model].browse(activity_user.res_id).message_subscribe(partner_ids=[partner_id])
        self.env[activity.res_model].browse(activity.res_id).message_subscribe(
            partner_ids=[activity.user_id.partner_id.id])
        if activity.date_deadline and activity.date_deadline <= fields.Date.today():
            self.env['bus.bus']._sendone('Success',
                                         (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                                         {'type': 'activity_updated', 'activity_created': True})
        return activity


        # Override Mail Activity Unlink
    # @api.multi
    def unlink(self):
        # self._check_access('unlink')
        for activity in self:
            activity.ks_attachment_ids.unlink()
            if activity.date_deadline:
                if activity.date_deadline and activity.date_deadline <= fields.Date.today():
                    self.env['bus.bus']._sendone('Success',
                        (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                        {'type': 'activity_updated', 'activity_deleted': True})
        return super(MailActivity, self.sudo()).unlink()

    #Override Mail Activity Write
    # @api.multi
    def write(self, values):
        # self._check_access('write')
        if values.get('user_id'):
            pre_responsibles = self.mapped('user_id.partner_id')
        res = super(MailActivity, self.sudo()).write(values)

        if values.get('user_id'):
            if values['user_id'] != self.env.uid:
                to_check = self.filtered(lambda act: not act.automated)
                to_check._check_access_assignation()
                if not self.env.context.get('mail_activity_quick_update', False):
                    self.action_notify()
            for activity in self:
                self.env[activity.res_model].browse(activity.res_id).message_subscribe(
                    partner_ids=[activity.user_id.partner_id.id])
                if activity.date_deadline and activity.date_deadline <= fields.Date.today():
                    self.env['bus.bus']._sendone('Success',
                        (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                        {'type': 'activity_updated', 'activity_created': True})
            for activity in self:
                if activity.date_deadline and activity.date_deadline <= fields.Date.today():
                    for partner in pre_responsibles:
                        self.env['bus.bus']._sendone('Success',
                            (self._cr.dbname, 'res.partner', partner.id),
                            {'type': 'activity_updated', 'activity_deleted': True})
        return res


odoo_create = MailActivity.create
ks_create = KsMailActivity.create
MailActivity.create = ks_create

odoo_unlink = MailActivity.unlink
ks_unlink = KsMailActivity.unlink
MailActivity.unlink = ks_unlink

odoo_write = MailActivity.write
ks_write = KsMailActivity.write
MailActivity.write = ks_write
