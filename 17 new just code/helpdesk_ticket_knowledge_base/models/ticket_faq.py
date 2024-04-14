# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class TicketFaq(models.Model):
    _name = "ticket.faq"
    _rec_name = "question"
    _order = "id desc"
    _description = 'Ticket Faq'

    question = fields.Char(
        string="Question",
        required=True,
    )
    answer = fields.Html(
        string='Answer'
    )
    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.support',
        string="Helpdesk Ticket",
        readonly=True,
    )
    question_url = fields.Char(
        string="URL",
    )
    category_id = fields.Many2one(
        "ticket.faq.category",
        string="Category"
    )
    tag_ids = fields.Many2many(
        "ticket.faq.tags",
        string="Tags"
    )
