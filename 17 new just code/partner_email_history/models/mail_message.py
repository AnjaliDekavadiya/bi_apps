# -*- coding: utf-8 -*-
# from openerp import fields, models, api
from odoo import fields, models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.depends('res_id', 'model')
    def _compute_partners(self):
        for msg in self:
            record_id = msg.res_id
            record_model = msg.model
            if record_id and record_model:
                record = self.env[record_model].browse(record_id)
                if 'message_follower_ids' in record._fields:
                    partner_ids = []
                    for follower in record.message_follower_ids:
                        if follower.partner_id:
                            partner_ids.append(follower.partner_id.id)
                    msg.follower_partner_ids = partner_ids

    follower_partner_ids = fields.Many2many(
        'res.partner',
        'res_partner_follower_mail_message_rel',
        'message_id',
        'partner_id',
        string="Follower Partners",
        compute="_compute_partners",
        store=True,
        readonly=True,
    )
