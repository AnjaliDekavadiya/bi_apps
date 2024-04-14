from odoo import fields, models, api, _


class DxSaasDbFilterDownloadWizard(models.TransientModel):
    _name = 'dx.saas.dbfilter.download.wizard'
    _description = 'Download backup format wizard'

    format_type = fields.Selection([
        ("zip", "ZIP"),
        ("dump", "Dump")], string="Backup Format", index=True, required=True, default="dump")

    def backup_database_now(self):
        subscription = self.env["dx.saas.dbfilter.subscriptions"].search([("id", "=", self._context["active_id"])])
        if subscription:
            subscription.message_post(body=_('Backup Created Successfully by %s' % self.env.user.name))
            link = '/database/backup_now/%s/%s/%s' % (subscription.id, subscription.server_id.id, self.format_type)
            return {
                'type': 'ir.actions.act_url',
                'url': link,
                'target': 'self',
            }