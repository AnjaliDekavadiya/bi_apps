# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class TicketFaqTags(models.Model):
    _name = "ticket.faq.tags"
    _description = "Ticket Faq Tags"

    name = fields.Char(
        string="Name",
        required=True,
    )
