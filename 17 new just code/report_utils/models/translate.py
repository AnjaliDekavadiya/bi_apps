# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReportingCustomTemplateTranslateTerm(models.Model):
    _name = 'reporting.custom.template.translate.term'

    translate_from = fields.Char(string="From", required=True)
    translate_to = fields.Char(string="To", required=True)
    report_line_id = fields.Many2one('report.template.line', ondelete='cascade')
