# -*- coding: utf-8 -*-

from odoo import models, fields


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'
    
    ticket_solution = fields.Html(
       string='Ticket Solution'
   )
    image1 = fields.Binary(
        string="Solution Image 1",
    )
    image2 = fields.Binary(
        string="Solution Image 2",
    )
    image3 = fields.Binary(
        string="Solution Image 3",
    )
    image4 = fields.Binary(
        string="Solution Image 4",
    )
    image5 = fields.Binary(
        string="Solution Image 5",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
