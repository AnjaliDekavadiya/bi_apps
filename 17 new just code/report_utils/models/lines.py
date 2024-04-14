# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReportingTemplateTemplateLine(models.Model):
    _name = 'report.template.line'

    sequence = fields.Integer('Sequence', default=0)
    report_id = fields.Many2one('report.template', ondelete='cascade')
    model_id = fields.Many2one('ir.model', readonly=True)
    name_technical = fields.Char()
    name = fields.Char(string="Name")
    type = fields.Selection([
        ('row', 'Row'),
        ('fields', 'Fields'),
        ('address', 'Address'),
        ('lines', 'Lines'),
        ('options', 'Opti 0ons'),
        ('signature_boxes', 'Signature Boxes'),
        ('translate_terms', 'Translated Terms'),
    ])
    multi_lang_enabled = fields.Boolean()
    # color = fields.Char()
    field_ids = fields.One2many('report.template.line.field', 'report_line_id')
    option_field_ids = fields.One2many('report.template.options.field', 'report_line_id')
    signature_box_ids = fields.One2many('report.template.signature.box', 'report_line_id')
    row_ids = fields.One2many('report.template.row.col', 'report_line_id')
    preview_img = fields.Char() # DEPRECATED
    data_field_names = fields.Char()
    note = fields.Html()
    translate_term_ids = fields.One2many("reporting.custom.template.translate.term", "report_line_id")

    # @api.model
    # def create(self, vals):
    #     res = super(ReportingTemplateTemplateLine, self).create(vals)
    #     for each in res:
    #         each.color = '#499df1'
    #     return res

