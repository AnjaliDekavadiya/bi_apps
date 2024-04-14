# -*- coding: utf-8 -*-
#from openerp import models, api, fields, _ odoo13
from odoo import models, api, fields, _

class HelpdeskSearchQuestionWizard(models.TransientModel):
    _name = "helpdesk.search.question.wizard"
    _description = "Helepdesk Search Question"

    ticket_faq_ids = fields.Many2many(
        "ticket.faq",
        string="Question & Answers"
    )
