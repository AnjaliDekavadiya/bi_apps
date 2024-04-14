# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    custom_ref = fields.Char(
        string="Referred By"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: