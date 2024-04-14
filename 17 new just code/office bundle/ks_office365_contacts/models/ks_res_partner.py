from odoo import models, fields, api, _


class KsOdooContacts(models.Model):
    _inherit = "res.partner"

    ks_office_contact_id = fields.Char(default="", string='Office Contact Id')
    ks_user_id = fields.Many2one('res.users', string='User Id')
    type = fields.Selection(selection_add=[('business', 'Business Address')])

    # @api.multi
    def copy(self):
        self.ks_office_contact_id = ""
        return super(KsOdooContacts, self).copy()

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if 'ks_user_id' not in val:
                val.update({'ks_user_id': self.env.user.id})
        return super(KsOdooContacts, self).create(vals_list)

    # @api.multi
    def unlink(self):
        for rec in self:
            if self.env.user.ks_sync_deleted_contact:
                self.env['ks.deleted'].create({
                    'name': rec.name,
                    'ks_odoo_id': rec.id,
                    'ks_office_id': rec.ks_office_contact_id,
                    'ks_module': 'contact',
                    'ks_user_id': self.env.user.id,
                })
        return super(KsOdooContacts, self).unlink()
