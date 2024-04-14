# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class TicketFaqCategory(models.Model):
    _name = "ticket.faq.category"
    _description = "Ticket Faq Category"

    name = fields.Char(
        string="Name",
        required=True,
    )
