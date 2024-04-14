# -*- coding: utf-8 -*-
from odoo import api, fields, models 


class ReportTemplateRowCol(models.Model):
    _name = 'report.template.row.col'
    _description = 'Report Template Rows'

    report_line_id = fields.Many2one('report.template.line', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    type_id = fields.Many2one('report.template.options.combo.box.item', domain="[('key', '=', 'report_utils__row_col_types')]")
    align_id = fields.Many2one('report.template.options.combo.box.item', domain="[('key', '=', 'report_utils__align')]")
    # width_id = fields.Many2one('report.template.options.range.item', domain="[('value', '>=', 1), ('value', '<=', 100)]", string="Width (%)")
    # padding_left_id = fields.Many2one('report.template.options.range.item', domain="[('value', '>=', 1), ('value', '<=', 100)]", string="Left Padding (Px)")
    # padding_right_id = fields.Many2one('report.template.options.range.item', domain="[('value', '>=', 1), ('value', '<=', 100)]", string="Right Padding (Px)")
    width = fields.Integer(string="Width (%)")
    padding_left = fields.Integer(string="Left Padding (Px)")
    padding_right = fields.Integer(string="Right Padding (Px)")

