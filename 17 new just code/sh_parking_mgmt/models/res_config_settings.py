# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_journal_id = fields.Many2one(
        comodel_name="account.journal", string="Payment Journal", domain="[('type', '=', 'cash')]")
    sh_default_user = fields.Many2one(
        comodel_name="res.partner", string="Default User", compute='_compute_default_user')
    sh_remaining_amount = fields.Float(string="Remaining Amount")

    def _compute_default_user(self):
        default_user = self.env.ref(
            'sh_parking_mgmt.res_partner_event_10')
        if default_user:
            self.sh_default_user = default_user.id
        else:
            self.sh_default_user = False


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_journal_id = fields.Many2one(
        comodel_name="account.journal", string="Paid Payment Journal", related='company_id.sh_journal_id', readonly=False, required=True)
    sh_default_user = fields.Many2one(
        comodel_name="res.partner", related='company_id.sh_default_user', string="Default User", required=True)
    sh_remaining_amount = fields.Float(
        string="Remaining Amount", readonly=False, required=True, related='company_id.sh_remaining_amount')
