# -*- coding: utf-8 -*-
from odoo import models, fields


class MsegatAccountSenderIds(models.Model):
    _name = 'msegat.account.sender.ids'
    _description = "Msegat account sender Ids"
    _rec_name = "sender_id"

    sender_id = fields.Char("Sender Id/Tag Name", copy=False, required=True, help="Sender Id/Tag Name")
    status = fields.Char("Status", copy=False, help="Status")
