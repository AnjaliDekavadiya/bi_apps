# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    custom_send_feedback_mail = fields.Boolean(
        string="Customer POS Feedback Email",
        copy=True,
        default=True,
        help="If this check box is ticked then system will send Feedback Request email to customer"
    )
