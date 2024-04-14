# -*- coding: utf-8 -*-
#from openerp import models, fields odoo13
from odoo import models, fields


class HelpdeskSupport(models.Model):
    _inherit = "helpdesk.support"

    ticket_faq_ids = fields.One2many(
        'ticket.faq',
        'helpdesk_ticket_id',
        string="Knowledge Base Q&A",
        readonly=True,
    )
