# -*- coding: utf-8 -*-
from odoo import api, fields, models 


class ReportCustomTemplateSignatureBox(models.Model):
    _name = 'report.template.signature.box'
    _description = 'Signature Box'

    report_line_id = fields.Many2one('report.template.line', ondelete='cascade')
    heading = fields.Char(string="Heading")
    heading_lang2 = fields.Char(string="Heading (Secondary Lang)")
    sequence = fields.Integer('Sequence', default=10)
