# -*- coding: utf-8 -*-
from odoo import api, fields, models

FIELD_SEPARATORS = [
    ('none', 'No Separator'),
    ('next_line', 'Next Line'),
    ('comma', 'Comma'),
]

ALIGNMENT_VALS = [
    ('left', 'Left'),
    ('center', 'Center'),
    ('right', 'Right'),
]


class ReportTemplateLineField(models.Model):
    _name = 'report.template.line.field'

    report_line_id = fields.Many2one('report.template.line', ondelete='cascade')
    report_line_type = fields.Selection(related='report_line_id.type')
    sequence = fields.Integer('Sequence', default=10)
    model_id = fields.Many2one('ir.model', related='report_line_id.model_id', readonly=True)
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_id)]")
    field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
    field_relation = fields.Char(related='field_id.relation', readonly=True)
    field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field", domain="[('model_id.model', '=', field_relation)]")
    label = fields.Char(string='Label')
    label_lang2 = fields.Char(string='Label (Secondary Lang)')
    start_with = fields.Selection(FIELD_SEPARATORS, string='Start With', default='next_line')
    null_value_display = fields.Boolean(string='Display Null')
    alignment = fields.Selection(ALIGNMENT_VALS, string='Alignment', default='left')
    null_hide_column = fields.Boolean(string='Hide Column if Null')
    thousands_separator = fields.Selection([('not_applicable', 'Not Applicable'), ('applicable', 'Applicable')], default='not_applicable')
    currency_field_expression = fields.Char(string='Currency Field')
    width = fields.Char(string='Width')
    remove_decimal_zeros = fields.Boolean(string="Remove Decimal Zeros", default=False)
    precision = fields.Integer(string="Decimal Points", default=2)
    visibility_condition = fields.Char()  # E.g record.state in ['draft', 'sent']


