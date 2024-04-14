# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MsegatSmsGroups(models.Model):
    _name = 'msegat.sms.groups'
    _description = "Msegat SMS Groups"

    @api.depends('recipients')
    def _compute_total_recipients(self):
        for sms_group_id in self:
            sms_group_id.recipients_count = len(sms_group_id.recipients)

    name = fields.Char("Group Name", help="Group name", required=True, copy=False)
    active = fields.Boolean("Active", default=True)
    recipients_count = fields.Integer(string='recipients Count', compute='_compute_total_recipients')
    recipients = fields.Many2many("res.partner", 'msegat_sms_groups_res_partner_rel', 'sms_group_id', 'partner_id',
                                  "Recipients", required=True)

    # Odoo Logic Section
    # =====================
    def action_view_recipients(self):
        """
            :return: action or error
        """
        recipients = self.env['res.partner'].sudo().search([('id', 'in', self.recipients.ids)])
        action = {
            'domain': "[('id', 'in', " + str(recipients.ids) + " )]",
            'name': "Recipients",
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
        }
        return action
