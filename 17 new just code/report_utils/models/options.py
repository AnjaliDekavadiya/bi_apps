# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get


def truncate_long_text(text):
    return text[:70] + (text[70:] and '...')


FIELD_TYPES = [
    ('char', 'Char'),
    ('text', 'Text'),
    ('html', 'Html'),
    ('color', 'Color'),
    ('boolean', 'Boolean'),
    ('integer', 'Integer'),
    ('combo_box', 'ComboBox'),
    ('break', 'Break'),
    ('image', 'Image'),
    ('binary', 'Binary'),
    ('range', 'Range'),
    ('timezone', 'Timezone'),
]


class ReportCustomTemplateOptionsField(models.Model):
    _name = 'report.template.options.field'

    sequence = fields.Integer('Sequence', default=0)
    report_line_id = fields.Many2one('report.template.line', ondelete='cascade')
    field_type = fields.Selection(FIELD_TYPES, required=True, default='char')
    name_technical = fields.Char()
    name = fields.Char(string="Description")
    value_display = fields.Char(string="Value", compute="_compute_value_display")
    # enable_lang2 = fields.Boolean()
    value_char = fields.Char()
    value_color = fields.Char()
    value_text = fields.Text()
    value_text2 = fields.Text()
    value_boolean = fields.Boolean()
    value_integer = fields.Integer()
    value_combo_box = fields.Many2one('report.template.options.combo.box.item', domain="[('key', '=', key_combo_box)]")
    key_combo_box = fields.Char()
    value_image = fields.Binary()
    value_binary = fields.Binary()
    value_range_ids = fields.Many2many('report.template.options.range.item', relation='report_options_range_possible_value_rel')
    value_range = fields.Many2one('report.template.options.range.item', domain="[('id', 'in', value_range_ids)]")
    value_timezone = fields.Selection(_tz_get)
    value_html = fields.Html()
    options = fields.Char()
    field_required = fields.Boolean(default=False)

    def get_value(self):
        self.ensure_one()
        if self.field_type == "char":
            return self.value_char or ""
        if self.field_type == "color":
            return self.value_color or ""
        elif self.field_type == "text":
            return self.value_text or ""
        elif self.field_type == "range":
            if self.value_range:
                value = self.value_range.value
            else:
                value = False
            return value
        elif self.field_type == "boolean":
            return self.value_boolean
        elif self.field_type == "integer":
            return self.value_integer
        elif self.field_type == "combo_box":
            return self.value_combo_box and self.value_combo_box.name_technical or False
        elif self.field_type == "break":
            return ""
        elif self.field_type == "image":
            return self.value_image
        elif self.field_type == "binary":
            return self.value_binary
        elif self.field_type == "timezone":
            return self.value_timezone
        elif self.field_type == "html":
            return self.value_html
        raise NotImplementedError()

    def _compute_value_display(self):
        for rec in self:
            value = rec.get_value()
            if rec.field_type == "boolean":
                value = value and "Yes" or "No"
            if value and rec.field_type == "text":
                value = truncate_long_text(value)
            if rec.field_type == "combo_box":
                value = rec.value_combo_box and rec.value_combo_box.name or "Undefined"
            if rec.field_type == "timezone":
                value = value or "Undefined"
            if rec.field_type == "image":
                value = value and "Uploaded" or "No Image"
            if rec.field_type == "binary":
                value = value and "Uploaded" or "No File"
            if rec.field_type == "html":
                value = ""
            if rec.field_type == "range":
                if not value and type(value) == bool:
                    value = "Undefined"
            rec.value_display = str(value)


class ReportCustomTemplateOptionsComboBoxItem(models.Model):
    _name = 'report.template.options.combo.box.item'

    name = fields.Char()
    name_technical = fields.Char()
    key = fields.Char()
    parameters = fields.Char()


class ReportTemplateOptionsRangeItem(models.Model):
    _name = 'report.template.options.range.item'
    _rec_name = "value"

    value = fields.Integer()

