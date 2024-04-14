# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.image import image_data_uri
from datetime import datetime
from dateutil import tz
from odoo.tools.safe_eval import safe_eval
import inspect

HEADER_OPACITY = 0.9


# DATE_FORMATS = [
#     ("01_%d %b %Y", "18 Feb 2020"),
#     ("02_%d/%b/%Y", "18/Feb/2020"),
#     ("03_%d %B %Y", "18 February 2020"),
#     ("04_%d/%m/%Y", "18/02/2020"),
#     ("05_%d/%m/%y", "18/02/20"),
#     ("06_%m/%d/%Y", "02/18/2020"),
#     ("07_%d-%b-%Y", "18-Feb-2020"),
#     ("08_%d. %b. %Y", "18.Feb. 2020"),
#     ("09_%b %d, %y", "Feb 18, 20"),
#     ("10_%B %d, %y", "February 18, 20"),
#     ("11_%b %d, %Y", "Feb 18, 2020"),
#     ("12_%B %d, %Y", "February 18, 2020"),
#     ("13_%A, %d %b %Y", "Tuesday, 18 Feb 2020"),
#     ("14_%A, %B %d, %Y", "Tuesday, February 18, 2020"),
#     ("15_%a, %B %d, %Y", "Tue, February 18, 2020"),
#     ("16_%a, %B %d, %y", "Tue, February 18, 20"),
#     ("17_%a, %b %d, %Y", "Tue, Feb 18, 2020"),
#     ("18_%a, %b %d, %y", "Tue, Feb 18, 20"),
# ]

#
# def float_range(start, stop, step=1.0):
#     result = []
#     count = start
#     while count <= stop:
#         result.append(round(count, 2))
#         count += step
#     return result


#
# class Font:
#     size = False
#     family = False
#     line_height = False
#
#     def __init__(self, size="16px"):
#         self.size = size
#         self.family = "none"
#         self.line_height = 0
#
#     def get_size(self, percent=None):
#         if not percent:
#             return False
#         result = self.size * percent / 100
#         return round(result)


def getattr_new(obj, attribute):
    o = obj
    for each in attribute.split('.'):
        o = getattr(o, each)
    return o

def remove_font_prefix_num(font_name):
    if not font_name:
        return font_name
    if font_name.split("-")[0].isnumeric():
        return lchop(font_name, font_name.split("-")[0] + "-")
    return font_name

# def set_precision(num, precision=2):
#     if type(num) == int:
#         return num
#
#     if type(num) == str:
#         num = float(num.replace(',', ''))
#
#     f = '%.'+str(precision)+'f'
#     return f % num


def remove_decimal_zeros_from_number(num):
    decimal = num - int(num)
    if not decimal:
        return int(num)
    return num


def lchop(s, suffix):

    if suffix and s.startswith(suffix):
        return s[len(suffix):]
    return s


def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def get_all_font_list(with_extension=False):
    vals = []
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.dirname(dir_path) + '/static/fonts'
    for each in os.listdir(dir_path):
        if each.endswith('ttf'):
            font = each
            if not with_extension:
                font = rchop(font, ".ttf")
            vals.append((font, font))
    return sorted(vals)


def add_timezone(d, timezone):
    if not timezone:
        return d
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(timezone)

    utc = d.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def set_sequence(options):
    # foooooo

    # print(options)
    for i in range(len(options or [])):
        option = options[i]
        sequence_value = i + 1
        # print(option[2])

        # print(type(option) == dict)
        new_dict = {**option[2]}
        # new_dict = option[2].copy()
        new_dict['sequence'] = sequence_value
        options[i] = option[:2] + (new_dict,)

class ReportTemplate(models.Model):
    _name = 'report.template'
    _rec_name = 'name_display'

    DEFAULT_VALUES = {
        'page_number_type': 'page:1/n',
        # 'date_format': DATE_FORMATS[0][0],
    }

    WATERMARK_SAMPLE_LIST_HTML = """
    Sample Watermarks: <br/>
    <a target="_blank" href="/report_utils/static/watermarks/sample1.pdf">Download-Sample-Watermark-1.pdf</a><br/> 
    <a target="_blank" href="/report_utils/static/watermarks/sample2.pdf">Download-Sample-Watermark-2.pdf</a><br/> 
    <a target="_blank" href="/report_utils/static/watermarks/sample3.pdf">Download-Sample-Watermark-3.pdf</a><br/> 
    <a target="_blank" href="/report_utils/static/watermarks/sample4.pdf">Download-Sample-Watermark-4.pdf</a><br/> 
    <a target="_blank" href="/report_utils/static/watermarks/sample5.pdf">Download-Sample-Watermark-5.pdf</a><br/> 
    <a target="_blank" href="/report_utils/static/watermarks/sample6.pdf">Download-Sample-Watermark-6.pdf</a><br/> 
    <a target="_blank" href="/report_utils/static/watermarks/sample7.pdf">Download-Sample-Watermark-7.pdf</a><br/> 
    """

    name = fields.Char(required=True, string='Technical Name')
    name_display = fields.Char(required=True, string='Report Name')
    multi_company_applicable = fields.Boolean(default=False)
    multi_language = fields.Boolean("Multi Language", default=False)
    second_lang_id = fields.Many2one('res.lang', string="Secondary Language")
    company_id = fields.Many2one("res.company")
    # design_id = fields.Many2one('report.template.design') # Archived
    # date_format = fields.Selection(DATE_FORMATS) # Archived
    paperformat_id = fields.Many2one('report.paperformat', 'Paper Format', ondelete="restrict")
    page_number_type = fields.Selection([
        ('none', 'No Page Number'),
        ('page:1/n', 'Page: 1 / 10'),
    ], string="Page No Type")
    line_ids = fields.One2many('report.template.line', 'report_id')
    show_similar_apps = fields.Boolean(default=True)

    def add_thousands_separator(self, num, precision=2, separator=",", decimal_separator="."):
        
        separator = self.get_option_data('thousand_seperator') or separator
        decimal_separator = self.get_option_data('decimal_seperator') or decimal_separator

        if isinstance(num, int):
            result = '{:,}'.format(num)

        elif isinstance(num, float):
            f = '{:,.%sf}' % precision
            result = f.format(num)
        else:
            raise NotImplementedError()

        result = result.replace(",", "$comma")
        result = result.replace(".", "$dot")

        result = result.replace("$comma", separator)
        result = result.replace("$dot", decimal_separator)

        return result

    # def add_thousands_separator(self, num, precision=2, separator=",", decimal_separator="."):
    #
    #     if type(num) == int:
    #         return '{:,}'.format(num)
    #     f = '{:,.%sf}' % precision
    #     return f.format(num)

    def list_multi_language_options(self):
        return {}

    def get_standard_multi_language_options(self):
        return {
            'line_ids': [
                "section_header_address_lang2",
            ],
            'option_field_ids': [
                "lines_label_lang2",
                "serial_number_heading_lang2",
                "product_image_column_heading_lang2",
                "font_family2",
                "label_partner_lang2",
            ],
        }

    def remove_multi_lang_options(self):
        self.ensure_one()
        options = self.list_multi_language_options()[self.name]

        for line in self.line_ids:
            if line.name_technical in options['line_ids']:
                line.unlink()

            for o in line.option_field_ids:
                if o.name_technical in options['option_field_ids']:
                    o.unlink()

    def insert_multi_lang_options(self):
        options = self.list_multi_language_options()[self.name]

        data = self.get_report_list()[self.name]
        self.modify_data(data)

        for line in data['lines']:
            line_id = self.line_ids.filtered(lambda l:l.name_technical == line['name_technical'])

            if line['name_technical'] in options['line_ids'] and not line_id:
                self.line_ids = [(0, 0, line)]

            for o in line.get('option_field_ids', []):
                o_id = line_id.option_field_ids.filtered(lambda l: l.name_technical == o[2]['name_technical'])

                if o[2]['name_technical'] in options['option_field_ids'] and not o_id:
                    line_id.option_field_ids = [(0, 0, o[2])]

    def update_multi_lang_config(self):
        self.ensure_one()

        new_value = (not self.multi_language) if self._context.get('toggle') else self.multi_language

        if new_value:
            self.insert_multi_lang_options()
        else:
            self.remove_multi_lang_options()

        self.multi_language = new_value
        for line in self.line_ids:
            line.multi_lang_enabled = new_value

        #     for x in line.option_field_ids:
        #         x.enable_lang2 = new_value

    def reset_defaults(self):
        self.ensure_one()
        self.write(self.DEFAULT_VALUES)

    def modify_data(self, data):
        line_count = 0
        for line in data['lines']:
            line_count += 1

            # Add sequence
            line['sequence'] = line_count
            # if line.get('option_field_ids'):
            #     line2_count = 0
            #     for o in line.get('option_field_ids'):
            #         line2_count += 1
            #         o[2]['sequence'] = line2_count

            set_sequence(line.get('option_field_ids'))

            # Update Model
            if line.get('model_id'):
                line['model_id'] = self.env["ir.model"].search([("model", "=", line['model_id'])]).id

            # Update Fields
            if line.get('field_ids'):
                for x in line.get('field_ids'):

                    # Normal Fields
                    field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_id']), ('model_id', '=', line['model_id']),])
                    x[2]['field_id'] = field_id.id

                    # Display Fields
                    if x[2].get('field_display_field_id'):
                        display_field_id = self.env["ir.model.fields"].search([('name', '=', x[2]['field_display_field_id']), ('model_id', '=', self.env["ir.model"].search([('model', '=', field_id.relation)]).id),])
                        x[2]['field_display_field_id'] = display_field_id.id

            # Update Option Fields
            if line.get('option_field_ids'):

                for x in line.get('option_field_ids'):

                    # Combo
                    if x[2]['field_type'] == "combo_box":
                        if x[2].get('value_combo_box'):
                            combo_box = self.env['report.template.options.combo.box.item'].search([('name_technical', '=', x[2]['value_combo_box']), ('key', '=', x[2].get('key_combo_box') or x[2]['name_technical']),])
                            x[2]['value_combo_box'] = combo_box.id
                        else:
                            x[2]['value_combo_box'] = False

                    # Range
                    if x[2]['field_type'] == "range":

                        options = x[2]['options']
                        range_value_ids = self.get_range_possible_ids(start=options['range_start'], end=options['range_end'], step=options.get('step') or 1)

                        x[2]['value_range_ids'] = range_value_ids.ids

                        if x[2]['value_range'] or type(x[2]['value_range']) in (int, float):
                            range_id = self.env["report.template.options.range.item"].search([('value', '=', int(x[2]['value_range']))])
                            x[2]['value_range'] = range_id.id

            # Update Row Fields
            if line.get('row_ids'):
                for x in line.get('row_ids'):
                    x[2]['type_id'] = self.env['report.template.options.combo.box.item'].search([('name_technical', '=', x[2]['type_id']), ('key', '=', 'report_utils__row_col_types')]).id
                    x[2]['align_id'] = x[2].get('align_id') and self.env['report.template.options.combo.box.item'].search([('name_technical', '=', x[2]['align_id']), ('key', '=', 'report_utils__align')]).id
                    # x[2]['padding_left_id'] = x[2].get('padding_left_id') and self.env['report.template.options.range.item'].search([('value', '=', x[2]['padding_left_id'])]).id
                    # x[2]['padding_right_id'] = x[2].get('padding_right_id') and self.env['report.template.options.range.item'].search([('value', '=', x[2]['padding_right_id'])]).id

    def get_range_possible_ids(self, start, end, step=1):
        vals = list(range(int(start), int(end+1), int(step)))
        domain = [('value', 'in', vals)]

        if 0 in vals:
            domain = ['|', ('value', 'in', vals), ('value', '=', 0)]

        return self.env["report.template.options.range.item"].search(domain)

    def reset_template(self, report_name=None, company_id=None):
        if not company_id:
            company_id = self.company_id

        # Avoid Context From Button
        if type(report_name) == dict:
            report_name = report_name['report_name']

        report_name = report_name or self._context['report_name']
        report_list = self.get_report_list()
        data = report_list[report_name]

        # design_id = self.env['report.template.design'].search([
        #     ('name_technical', '=', data['template']),
        #     ('report_name', '=', report_name),
        # ])

        self.modify_data(data)

        vals = {
                'name': report_name,
                'name_display': data['name_display'],
                'multi_company_applicable': data.get('multi_company_applicable'),
                'company_id': company_id and company_id.id,
                # 'design_id': design_id.id,
                'paperformat_id': data.get('paperformat_id') or False,
                'line_ids': [(0, 0, x) for x in data['lines']],
        }

        report_id = self.get_template(report_name, company_id=company_id)

        if report_id:
            report_id.line_ids.unlink()
            # report_id.line_ids = False
            # print(vals)
            report_id.write(vals)
        else:
            report_id = self.create(vals)

        # print(len(report_id.line_ids.filtered(lambda x:x.name_technical == "section_label").option_field_ids))
        report_id.reset_defaults()
        # print(len(report_id.line_ids.filtered(lambda x:x.name_technical == "section_label").option_field_ids))
        report_id.update_multi_lang_config()

        self.reload_font_family()

    def reload_font_family(self):
        fonts = get_all_font_list()

        key = 'report_utils__font_family'
        item_obj = self.env['report.template.options.combo.box.item']
        to_be_deleted = item_obj.search([('key', '=', key), ('name_technical', 'not in', [f[0] for f in fonts])])

        to_be_deleted.unlink()

        for each in fonts:
            record = item_obj.search([('key', '=', key), ('name_technical', '=', each[0])])

            if not record:
                item_obj.create({
                    'name': remove_font_prefix_num(each[0]),
                    'name_technical': each[0],
                    'key': key,
                })

    def console_template(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'report.template.console',
            'target': 'new',
            'view_mode': 'form',
            'context': {'report_id': self.id}
        }

    def get_template(self, name, company_id=None):

        domain = [
            ('name', '=', name.strip()),
            # ('design_id', '!=', False),
        ]
        if company_id:
            domain.append(('company_id', '=', company_id.id))
        return self.search(domain, limit=1)

    # def get_watermark_style(self, opacity, size, left=0):
    #     self.ensure_one()
    #     style = "position:absolute;left:{left}%;width:{size};height:auto;padding-top:40px;opacity:{opacity};".format(
    #         opacity=(opacity or 22) / 100,
    #         size=str(size or 400) + "px",
    #         left=left,
    #     )
    #     return style

    def get_field_data(self, obj, field_id, display_field=None, currency_field_name=None, thousands_separator=None, remove_decimal_zeros=None, precision=2):
        self.ensure_one()

        if not field_id:
            raise UserWarning('FieldNotFound')

        value = getattr(obj, field_id.name)

        result = value
        if field_id.ttype == 'char':
            result = value or ""
        elif field_id.ttype == 'many2one':
            if not value:
                result = ""
            else:
                result = value.display_name
                if display_field:
                    result = getattr(value, display_field)

        elif field_id.ttype == 'date':
            # date_format = self.date_format or DATE_FORMATS[0][0]
            date_format = self.get_date_format().name_technical

            result = ""
            if value:
                result = value.strftime(date_format.split('_')[1]) or ""

        elif field_id.ttype == 'datetime':
            if not value:
                result = ""
            else:
                date_format = self.get_date_format().name_technical
                # date_format = self.date_format or DATE_FORMATS[0][0]
                d = value.strftime(date_format.split('_')[1]) or ""
                t = value.strftime("%H:%M:%S") or ""
                result = "%s %s" % (d, t)

        elif field_id.ttype in ['float', 'integer']:

            if remove_decimal_zeros:
                value = remove_decimal_zeros_from_number(value)

            if thousands_separator and thousands_separator == 'applicable':
                value = self.add_thousands_separator(value, precision=precision)

            # value = set_precision(value, precision=precision)
            result = value

        elif field_id.ttype == 'many2many':
            value = ', '.join(map(lambda x: (display_field and getattr(x, display_field) or x.display_name), value))
            result = value
        elif field_id.ttype == 'monetary':
            if remove_decimal_zeros:
                value = remove_decimal_zeros_from_number(value)

            if thousands_separator and thousands_separator == 'applicable':
                value = self.add_thousands_separator(value, precision=precision)

            # value = set_precision(value, precision=precision)

            with_currency = str(value)

            curr_field = currency_field_name or 'currency_id'
            currency_id = getattr_new(obj, curr_field)
            if currency_id:
                if currency_id.position == 'before':
                    with_currency = currency_id.symbol + ' ' + with_currency
                else:
                    with_currency = with_currency + ' ' + currency_id.symbol
            result = with_currency

        result = self.update_translation(result)
        return result and str(result)

    def update_translation(self, text):
        self.ensure_one()
        if not text or type(text) != str:
            return text
        for line in self.line_ids.filtered(lambda x: x.type == "translate_terms"):
            for term in line.translate_term_ids:
                if term.translate_from.strip() == text.strip():
                    return term.translate_to.strip()
        return text

    @staticmethod
    def get_field_label(field_id, label=None, label_auto=False):
        label = label and label.strip()
        if not label and label_auto:
            label = field_id.field_description
        return label

    def get_fields_ids_data(self, obj, name_technical, label_auto=False):
        self.ensure_one()
        line_id = self.line_ids.filtered(lambda x: x.name_technical == name_technical)

        data = {'content': [], 'header': []}

        # Header
        for line in line_id.field_ids.sorted(key=lambda r: r.sequence):
            if not line.field_id:
                continue

            data['header'].append({
                'field_name': line.field_id.name,
                'label': self.get_field_label(field_id=line.field_id, label=line.label, label_auto=label_auto),
                'label_lang2': line.label_lang2,
                'null_hide_column': line.null_hide_column,
                'visibility_condition': line.visibility_condition,
                'invisible': False,
                'width_style': 'width:%s;' % (line.width or 'auto'),
            })

        # Content
        # Fixme "If object is null, IndexError: list index out of range"

        for each in obj:

            vals = []  # Todo: include meta data of row (eg. display_type)

            for line in line_id.field_ids.sorted(key=lambda r: r.sequence):
                # if name_technical == "section_employee_address":
                #     print(line.field_id)
                if not line.field_id:
                    continue

                value = self.get_field_data(obj=each, field_id=line.field_id, display_field=line.field_display_field_id.name, thousands_separator=line.thousands_separator, remove_decimal_zeros=line.remove_decimal_zeros, precision=line.precision)
                separator = {'next_line': '<br/>', 'comma': ','}.get(line.start_with, "")
                line_vals = {
                    'label': self.get_field_label(field_id=line.field_id, label=line.label, label_auto=label_auto),
                    'label_lang2': line.label_lang2,
                    'value': value,
                    'null_value_display': line.null_value_display,
                    'separator': separator,
                    'null_hide_column': line.null_hide_column,
                    'visibility_condition': line.visibility_condition,
                    'field_name': line.field_id.name,
                    'invisible': False,
                    'alignment_style': 'text-align:%s' % (line.alignment or 'left'),
                    'line_id': each,
                }

                if line_id.data_field_names:
                    for data_field_name in line_id.data_field_names.split(','):

                        if not data_field_name.strip():
                            continue

                        field_id = self.env["ir.model.fields"].search([('name', '=', data_field_name), ('model_id', '=', line_id.model_id.id), ])

                        if not field_id:
                            raise UserWarning("Field Not Found: %s (%s)" % (data_field_name, line_id.model_id.model))

                        value2 = self.get_field_data(obj=each, field_id=field_id)
                        line_vals[data_field_name] = value2

                vals.append(line_vals)


            data['content'].append(vals)  # fixme : merge list instead of append


        # Hide Column : Field Data
        field_data = {}
        for row in data['content']:
            for col in row:
                if not col['null_hide_column']:
                    continue
                field_name = col['field_name']
                value = col['value']
                if field_name in field_data:
                    field_data[field_name].append(value)
                else:
                    field_data[field_name] = [value]

        # Hide Column : Set Invisible (Content)
        for row in data['content']:
            for col in row:
                if not col['null_hide_column']:
                    continue
                val_list = field_data.get(col['field_name']) or []
                if not any(val_list):
                    col['invisible'] = True

        # Hide Column : Set Invisible (Header)
        for row in data['header']:
            if not row['null_hide_column']:
                continue

            val_list = field_data.get(row['field_name']) or []
            if not any(val_list):
                row['invisible'] = True

        return data

    def get_signature_data(self, technical_name):
        self.ensure_one()
        line_id = self.line_ids.filtered(lambda x: x.type == "signature_boxes" and x.name_technical == technical_name)
        if line_id:
            return line_id[0].signature_box_ids
        return False

    # def get_signature_td_style(self, data):
    #     if not data:
    #         return ""
    #     return "width:%spx" % round(100/len(data), 1)

    def get_design_id(self):
        self.ensure_one()
        res = None
        for line in self.line_ids.filtered(lambda x: x.type == "options"):
            for each in line.option_field_ids:
                if each.name_technical == "template_design":
                    res = each.value_combo_box

        if not res:
            return self.env.ref('report_utils.data_options_combo_box_design_pink')
        return res

    def get_date_format(self):
        self.ensure_one()
        res = None
        for line in self.line_ids.filtered(lambda x: x.type == "options"):
            for each in line.option_field_ids:
                if each.name_technical == "date_format":
                    res = each.value_combo_box
        if not res:
            return self.env.ref('report_utils.data_options_combo_box_date_format_1')
        return res

    def get_parameters(self):
        self.ensure_one()

        class ParametersObject:
            pass
        
        parameters = ParametersObject()

        design_id = self.get_design_id()

        if not design_id:
            raise UserError("Couldn\'t find design.")

        for key, value in literal_eval(design_id.parameters).items():
            setattr(parameters, key, value)

        parameters.mode = "colorful" # Fixme

        return parameters

    # def get_font(self):
    #     self.ensure_one()
    #     font = Font()
    #     font.size = False
    #     font.family = False
    #     font.line_height = False
    #     return font

    # def get_standard_font_style(self):
    #     self.ensure_one()
    #     font = self.get_font()
    #
    #
    #     style = ""
    #
    #     if font.line_height:
    #         style += ";line-height:" + str(font.line_height / 10) or "unset"
    #     if font.family:
    #         style += ";font-family:" + font.family or "unset"
    #     if font.size:
    #         style += ";font-size:" + to_pixel(font.size)
    #
    #     return style

    # def get_standard_label_style(self, font_weight='normal', color=None, case=None):
    #     self.ensure_one()
    #     font = self.get_font()
    #
    #     style = ""
    #     if font.size:
    #         style += ";font-size:" + to_pixel(font.get_size(percent=112))
    #     if font_weight:
    #         style += ";font-weight:" + font_weight
    #     if color:
    #         style += ";color:" + color
    #     if case:
    #         style += ";text-transform:" + case
    #
    #     return style

    @staticmethod
    def get_amount_in_text(obj, field_name, currency_field='currency_id'):
        currency_id = getattr_new(obj, currency_field)
        if not currency_id:
            return ""

        amount = getattr_new(obj, field_name)
        text = currency_id.amount_to_text(amount)

        return text

    def get_option_data(self, technical_name):
        self.ensure_one()

        for line in self.line_ids.filtered(lambda x: x.type == "options"):
            for each in line.option_field_ids:
                if each.name_technical == technical_name:
                    return each.get_value()

        for line in self.line_ids.filtered(lambda x: x.type == "row"):
            if line.name_technical == technical_name:
                row_list = []
                for r in line.row_ids.sorted(lambda x:x.sequence):
                    row_list.append({
                        'type': r.type_id.name_technical,
                        'align': r.align_id.name_technical or "left",
                        'width': r.width and f'{r.width}%' or "auto",
                        'padding_left': self.to_pixel(r.padding_left or 0),
                        'padding_right': self.to_pixel(r.padding_right or 0),
                    })

                return row_list


    # def get_header_footer_layout(self, technical_name, default=""):
    #     # Archived
    #     self.ensure_one()
    #     layout = self.get_option_data(technical_name) or default
    #     vals = {}
    #     for each in layout.split(','):
    #         vals[each.split('@')[1]] = each.split('@')[0]
    #     return vals

    def parse_dictx(self, technical_name, default=""):
        """ Format: {col1:auto,col2:auto,col3:auto} """
        self.ensure_one()
        vals = {}

        # value = self.get_option_data(technical_name) or default
        value = technical_name or default

        if value.startswith('{') and value.endswith('}'):
            value = lchop(value, '{')
            value = rchop(value, '}')

            for each in value.split(','):
                vals[each.split(':')[0]] = each.split(':')[1]
        return vals

    @staticmethod
    def to_pixel(number):
        return str(number) + "px"

    @staticmethod
    def from_pixel(pixel):
        return literal_eval(rchop(pixel, 'px'))

    @staticmethod
    def find_percent(amount, percent=125):
        if not percent:
            return 0
        result = amount * percent / 100
        return round(result)

    def get_report_list(self):
        """Hook"""
        return {}

    def get_page_number_section(self):
        self.ensure_one()
        if self.page_number_type == "none":
            return ""
        return """Page: <span class="page"/> / <span class="topage"/>"""

    @staticmethod
    def _hasattr(obj, attribute):
        return hasattr(obj, attribute)

    def get_current_time(self, timezone=None):
        self.ensure_one()

        # date_format = self.get_option_data('date_format') or "01_%d %b %Y"
        now = add_timezone(datetime.now(), timezone=timezone)
        # date_format = (self.date_format or DATE_FORMATS[0][0]).split('_')[1]
        date_format = (self.get_option_data('date_format') or "01_%d %b %Y").split('_')[1]
        return now.strftime(date_format + " %H:%M:%S")

    def open_paperformat(self):
        if self.paperformat_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'report.paperformat',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': self.paperformat_id.id,
            }

    def check_installed(self, module_name):
        module_id = self.env['ir.module.module'].search([
            ('name', '=', module_name),
            ('state', '=', 'installed'),
        ])
        return bool(module_id)

    @staticmethod
    def html_to_text(html):
        if not html:
            return ""
        import lxml.html as lh
        from lxml.html.clean import clean_html
        doc = lh.fromstring(html)
        doc = clean_html(doc)
        return doc.text_content()

    @staticmethod
    def dict_to_css(data):
        css = ""
        for k, v in data.items():
            css += "%s:%s;" % (k, v)
        return css

    @staticmethod
    def css_to_dict(css):
        my_dict = {}
        for each in css.split(';'):
            if ':' not in each:
                continue
            my_dict[each.split(':')[0]] = each.split(':')[1]
        return my_dict

    def hex_to_rgba(self, hex, opacity=1):
        hex = hex.lstrip('#')
        res = [int(hex[i:i + 2], 16) for i in (0, 2, 4)]
        res.append(opacity)
        return "rgba{}".format(tuple(res))

    def get_report_data_standard(self, template, rec):
        parameters = template.get_parameters()
        _option = template.get_option_data

        line_height = ((_option('font_line_height') or 0) / 10) or "unset"
        font = {'line-height': line_height, 'font-family': remove_font_prefix_num(_option('font_family')) or "unset", 'font-size': template.to_pixel(_option('font_size') or 16), 'direction': _option('direction'), 'text-align': {'RTL': 'right'}.get(_option('direction')) or 'left'}
        font_lang2 = font.copy()

        if self.multi_language and _option('font_family2'):
            font_lang2['font-family'] = remove_font_prefix_num(_option('font_family2'))

        if _option('apply_custom_color'):
            parameters.color1 = _option('custom_color1')
            parameters.color2 = _option('custom_color2')
            font['color'] = _option('custom_color_font') or "black"


        header_style = template.dict_to_css({'color': parameters.color1, 'background': template.hex_to_rgba(parameters.color2, opacity=HEADER_OPACITY)})

        if not _option('show_header_background'):
            header_style = template.css_to_dict(header_style)
            header_style["background"] = "transparent"
            header_style = template.dict_to_css(header_style)

        footer_style = template.dict_to_css({'color': parameters.color1, 'background': template.hex_to_rgba(parameters.color2, opacity=HEADER_OPACITY)})

        if not _option('show_footer_background'):
            footer_style = template.css_to_dict(footer_style)
            footer_style["background"] = "transparent"
            footer_style = template.dict_to_css(footer_style)

        if _option('show_table_header_background'):
            lines_header_style = template.dict_to_css({'color': 'white', 'background': template.hex_to_rgba(parameters.color1, opacity=HEADER_OPACITY)})
        else:
            lines_header_style = template.dict_to_css({'color': parameters.color1, 'background': 'white', 'border': '1px solid '+parameters.color1, })

        res = {}

        for line in [l for l in template.line_ids if l.type == "options"]:
            for option in [o for o in line.option_field_ids if o.name_technical not in ["-1"]]:
                res[option.name_technical] = _option(option.name_technical)

        for line in [l for l in template.line_ids if l.type == "row"]:
            res[line.name_technical] = _option(line.name_technical)

        for option in self.list_multi_language_options()[template.name].get('option_field_ids') or []:
            res[option] = _option(option)

        res['company_id'] = getattr(rec, 'company_id', False)
        res['reference_number'] = f"{_option('label_record_reference') or ''} {getattr(rec, 'name', '')}"
        res['parameters'] = parameters
        res['font'] = font
        res['header_style'] = header_style
        res['footer_style'] = footer_style
        res['standard_font'] = template.dict_to_css(font)
        res['standard_font_lang2'] = template.dict_to_css(font_lang2)
        res['label_style'] = template.dict_to_css({'font-size': template.to_pixel(template.find_percent(_option('font_size') or 16, percent=112)), 'font-weight': _option('label_font_weight'), 'color': parameters.color1, 'text-transform': _option('label_case'), })
        res['lines_header_style'] = lines_header_style

        # res = {
            # 'company_id': getattr(rec, 'company_id', False),
            # 'reference_number': 'No: %s' % getattr(rec, 'name', ""),
            # 'show_header': _option('show_header'),
            # 'show_footer': _option('show_footer'),
            # 'show_header_background': _option('show_header_background'),
            # 'show_footer_background': _option('show_footer_background'),
            # 'show_header_border_line': _option('show_header_border_line'),
            # 'show_footer_border_line': _option('show_footer_border_line'),
            # 'header_img': _option('header_image'),
            # 'parameters': parameters,
            # 'font': font,
            # 'header_layout': _option('header_layout'),
            # 'footer_layout': _option('footer_layout'),
            # 'header_style': header_style,
            # 'footer_img': _option('footer_image'),
            # 'logo_style': _option('logo_style') or 'width:auto;height:80px;',
            # 'logo_image': _option('logo_image'),
            # 'show_logo': _option('show_logo'),
            # 'footer_style': footer_style,
            # 'standard_font': template.dict_to_css(font),
            # 'standard_font_lang2': template.dict_to_css(font_lang2),
            # 'direction': _option('direction'), # Archived
            # 'label_style': template.dict_to_css({'font-size': template.to_pixel(template.find_percent(_option('font_size'), percent=112)), 'font-weight': _option('label_font_weight'), 'color': parameters.color1, 'text-transform': _option('label_case'), }),
            # 'lines_header_style': lines_header_style,
            # 'show_print_time': _option('show_print_time'),
            # 'report_timezone': _option('report_timezone'),
            # 'padding_after_header': _option('padding_after_header'),
            # 'padding_before_lines': _option('padding_before_lines'),
            # 'show_serial_number': _option('show_serial_number'),
            # 'serial_number_heading': _option('serial_number_heading'),
            # 'serial_number_heading_lang2': _option('serial_number_heading_lang2'),
            # 'show_product_image': _option('show_product_image'),
            # 'product_image_position': _option('product_image_position'),
            # 'product_image_column_heading': _option('product_image_column_heading'),
            # 'product_image_width': _option('product_image_width'),
            # 'show_amount_in_text': _option('show_amount_in_text'),
            # 'label_amount_in_text': _option('label_amount_in_text'),
            # 'show_company_tagline_footer': _option('show_company_tagline_footer'),
            # 'section_signature_box': _option('section_signature_box'),

            # 'label_partner': _option('label_partner'),
            # 'label_partner_lang2': _option('label_partner_lang2'),
            # 'lines_label': _option('lines_label'),
            # 'lines_label_lang2': _option('lines_label_lang2'),
            # 'show_note': _option('show_note'),
            # 'show_payment_communication': _option('show_payment_communication'),
            # 'extra_terms': _option('extra_terms'),
            # 'show_extra_terms_next_page': _option('show_extra_terms_next_page'),
        # }


        return res

    # @staticmethod
    # def dict_remove_null(my_dict):
    #     return {k: my_dict[k] for k in my_dict if my_dict[k]}

    # def get_standard_header_style(self, parameters):
    #     css = dict()
    #
    #     # print(parameters)
    #     if parameters.mode == "colorful":
    #         css['color'] = parameters.color1
    #         css['background'] = parameters.color2
    #
    #     elif parameters.mode == "plain":
    #         css['color'] = parameters.color1
    #         css['background'] = 'white'
    #
    #     return self.dict_to_css(css)
    #
    #
    #     # if parameters.mode == "colorful":
    #     #     return "color:{color1};background:{color2};".format(color1=color1, color2=color2)
    #     #
    #     # elif parameters.mode == "plain":
    #     #     return "color:{color1};background:white;".format(color1=color1, color2=color2)

    @staticmethod
    def get_line_display_type(lines, return_value=False):
        value = False
        for line in lines:
            if 'display_type' not in line:
                return False

            if return_value:
                value = line['line_id'].name
            else:
                value = line['display_type']
        return value
    
    def merge_css(self, *args):
        my_dict = {}
        for css in args:
            my_dict.update(self.css_to_dict(css))
        return self.dict_to_css(my_dict)

    @staticmethod
    def newline_to_br(text, strip=True):
        text = text or ""
        if strip:
            text = text.strip()
        return text.replace('\n', '<br/>')

    def get_watermark_pdf_list(self):
        """Hook"""
        return {}

    def get_watermark_pdf(self, report_name):
        data = self.get_watermark_pdf_list() or {}
        return data.get(report_name)

    def close_similar_apps(self):
        self.show_similar_apps = False

    @staticmethod
    def pixel_to_break(pixel):
        if pixel > 0:
            return """ <div style="height:{}px"/> """.format(pixel)
        return ""

    def get_standard_report_line(self, name, additional=None):
        options_separator = (0, 0, {'field_type': 'break', 'name_technical': '-1', 'name': '-', })

        if name == "section_general":

            return {
                'name': 'General',
                'name_technical': 'section_general',
                'type': 'options',
                'preview_img': 'information.png',
                'option_field_ids': [
                        (0, 0, {'field_type': 'combo_box', 'name_technical': 'template_design', 'key_combo_box': 'report_utils__template_design', 'name': 'Design', 'value_combo_box': 'dark_red', 'field_required': True}),
                        (0, 0, {'field_type': 'combo_box', 'name_technical': 'date_format', 'key_combo_box': 'report_utils__date_format', 'name': 'Date Format', 'field_required': True}),
                        (0, 0, {'field_type': 'char', 'name_technical': 'thousand_seperator', 'name': 'Amount Thousand Seperator', 'value_char': ','}),
                        (0, 0, {'field_type': 'char', 'name_technical': 'decimal_seperator', 'name': 'Amount Decimal Seperator', 'value_char': '.'}),

                ]
            }

        elif name == "section_header_layout":
            return {
                'name': 'Header Layout',
                'name_technical': 'header_layout',
                'type': 'row',
                'preview_img': '1_top.png',
                'row_ids': [
                        (0, 0, {'type_id': 'address', 'align_id': 'left', 'width': '35', 'padding_left': 20}),
                        (0, 0, {'type_id': 'logo', 'align_id': 'center', 'width': '30'}),
                        (0, 0, {'type_id': 'heading', 'align_id': 'right', 'width': '35', 'padding_right': 20}),
                ]
            }

        elif name == "section_footer_layout":
            return {
                'name': 'Footer Layout',
                'name_technical': 'footer_layout',
                'type': 'row',
                'preview_img': '5_bottom.png',
                'row_ids': [
                        (0, 0, {'type_id': 'address', 'align_id': 'left', 'padding_left': 20}),
                        (0, 0, {'type_id': 'tagline', 'align_id': 'center'}),
                        (0, 0, {'type_id': 'page_number', 'align_id': 'right', 'padding_right': 20}),
                        
                ]
            }

        elif name == "section_header_address":
            return {
                'name': 'Header Address (Default)',
                'name_technical': 'section_header_address',
                'model_id': 'res.company',
                'type': 'address',
                'preview_img': '1_top.png',
                'field_ids': [
                    (0, 0, {'start_with': False, 'sequence': 10, 'field_id': 'street', }),
                    (0, 0, {'start_with': 'next_line', 'sequence': 20, 'field_id': 'street2', }),
                    (0, 0, {'start_with': 'next_line', 'sequence': 30, 'field_id': 'city', }),
                    (0, 0, {'start_with': 'comma', 'sequence': 40, 'field_id': 'state_id', 'field_display_field_id': 'name', }),
                    (0, 0, {'start_with': 'comma', 'sequence': 50, 'field_id': 'zip', }),
                    (0, 0, {'start_with': 'next_line', 'sequence': 60, 'field_id': 'country_id', 'field_display_field_id': 'name', }),
                ],
            }

        elif name == "section_header_address_lang2":
            return {
                'name': 'Header Address (Secondary Lang)',
                'name_technical': 'section_header_address_lang2',
                'model_id': 'res.company',
                'type': 'address',
                'preview_img': '1_top.png',
                'field_ids': [
                    # (0, 0, {'start_with': False, 'sequence': 10, 'field_id': 'street', }),
                    # (0, 0, {'start_with': 'next_line', 'sequence': 20, 'field_id': 'street2', }),
                    # (0, 0, {'start_with': 'next_line', 'sequence': 30, 'field_id': 'city', }),
                    # (0, 0, {'start_with': 'comma', 'sequence': 40, 'field_id': 'state_id', 'field_display_field_id': 'name', }),
                    # (0, 0, {'start_with': 'comma', 'sequence': 50, 'field_id': 'zip', }),
                    # (0, 0, {'start_with': 'next_line', 'sequence': 60, 'field_id': 'country_id', 'field_display_field_id': 'name', }),
                ],
            }

        elif name == "section_footer":
            return {
                'name': 'Footer Address',
                'name_technical': 'section_footer_address',
                'model_id': 'res.company',
                'type': 'address',
                'preview_img': '5_bottom.png',
                'field_ids': [
                    (0, 0, {'label': 'Phone', 'sequence': 10, 'field_id': 'phone', 'start_with': 'none'}),
                    (0, 0, {'label': 'Email', 'sequence': 20, 'field_id': 'email'}),
                    (0, 0, {'label': 'Web', 'sequence': 30, 'field_id': 'website'}),
                    (0, 0, {'label': 'Tax ID', 'sequence': 40, 'field_id': 'vat'}),
                ],
            }

        elif name == "section_header_footer_images":
            return {
                'name': 'Header/Footer Images',
                'name_technical': 'section_header_footer_images',
                'type': 'options',
                'preview_img': '1_top_5_bottom.png',
                'option_field_ids': [
                    (0, 0, {'field_type': 'image', 'name_technical': 'header_image', 'name': 'Header'}),
                    (0, 0, {'field_type': 'image', 'name_technical': 'footer_image', 'name': 'Footer'}),
                ]
            }

        elif name == "section_header_footer_layout":
            option_field_ids = [
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_header', 'name': 'Show Header ?', 'value_boolean': True}),
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_footer', 'name': 'Show Footer ?', 'value_boolean': True}),
                    # options_separator,
                    # (0, 0, {'field_type': 'combo_box', 'name_technical': 'header_layout',
                    #         'key_combo_box': 'report_utils__header_layout', 'name': 'Header Layout',
                    #         'value_combo_box': self.env.ref(
                    #             'report_utils.data_options_combo_box_header_layout_auto_auto_auto').name_technical, }),
                    # (0, 0, {'field_type': 'combo_box', 'name_technical': 'header_section_sequence',
                    #         'key_combo_box': 'report_utils__header_section_sequence', 'name': 'Header Layout Order',
                    #         'value_combo_box': 'address_logo_reference', }),
                    # (0, 0, {'field_type': 'combo_box', 'name_technical': 'footer_layout',
                    #         'key_combo_box': 'report_utils__footer_layout', 'name': 'Footer Layout',
                    #         'value_combo_box': self.env.ref(
                    #             'report_utils.data_options_combo_box_footer_layout_30_40_30').name_technical, }),
                    options_separator,
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_header_background', 'name': 'Show Header Background?', 'value_boolean': True}),
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_footer_background', 'name': 'Show Footer Background?', 'value_boolean': True}),
                    options_separator,
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_header_border_line', 'name': 'Show Header Line?', 'value_boolean': True}),
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_footer_border_line', 'name': 'Show Footer Line?', 'value_boolean': True}),
                    options_separator,
                    (0, 0, {'field_type': 'boolean', 'name_technical': 'show_table_header_background', 'name': 'Show background for table header?', 'value_boolean': True}),
                    # options_separator,
                    # (0, 0, {'field_type': 'boolean', 'name_technical': 'show_company_tagline_footer',
                    #         'name': 'Show Company tagline Footer ?', 'value_boolean': True}),
            ]

            set_sequence(option_field_ids)
            return {
                'name': 'Header/Footer Advanced',
                'name_technical': 'section_header_footer_layout',
                'type': 'options',
                'preview_img': '1_top_5_bottom.png',
                'option_field_ids': option_field_ids
            }

        elif name == "section_partner_address":
            return {
                'name': 'Customer Address',
                'name_technical': 'section_partner_address',
                'model_id': 'res.partner',
                'type': 'address',
                'preview_img': '2_left.png',
                'field_ids': [
                    (0, 0, {'start_with': False, 'sequence': 10, 'field_id': 'street', }),
                    (0, 0, {'start_with': 'next_line', 'sequence': 20, 'field_id': 'street2', }),
                    (0, 0, {'start_with': 'next_line', 'sequence': 30, 'field_id': 'city', }),
                    (0, 0,
                     {'start_with': 'comma', 'sequence': 40, 'field_id': 'state_id', 'field_display_field_id': 'name'}),
                    (0, 0, {'start_with': 'comma', 'sequence': 50, 'field_id': 'zip', }),
                    (0, 0, {'start_with': 'next_line', 'sequence': 60, 'field_id': 'country_id',
                            'field_display_field_id': 'name'}),
                ],
            }

        elif name == "section_amount_in_words":
            return   {'name': 'Amount In Words',
                 'name_technical': 'section_amount_in_words',
                 'type': 'options',
                 'preview_img': 'dollar.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_amount_in_text', 'name': 'Show Amount in Words ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'label_amount_in_text', 'name': 'Label Amount in Words', 'value_char': 'Amount In Words'}),
                 ],
                 }

        elif name == "section_watermark":
            return {
                'name': 'Watermark',
                'name_technical': 'section_watermark',
                'type': 'options',
                'preview_img': 'watermark.png',
                'option_field_ids': [
                    (0, 0, {'field_type': 'binary', 'name_technical': 'watermark_pdf', 'name': 'Watermark File (Pdf Only)'}),
                ],
                'note': self.WATERMARK_SAMPLE_LIST_HTML
            }

        elif name == "section_logo":
            return {'name': 'Logo',
             'name_technical': 'section_logo',
             'type': 'options',
             'preview_img': 'logo.png',
             'option_field_ids': [
                 (0, 0, {'field_type': 'combo_box', 'name_technical': 'logo_style',
                         'key_combo_box': 'report_utils__logo_style', 'name': 'Logo Style',
                         'value_combo_box': 'width:auto;height:80px;', }),
                 (0, 0, {'field_type': 'image', 'name_technical': 'logo_image', 'name': 'Change logo in report'}),
                 (0, 0, {'field_type': 'boolean', 'name_technical': 'show_logo', 'name': 'Show Logo ?',
                         'value_boolean': True}),
             ]
             }
        elif name == "section_font":
            return {'name': 'Font',
                    'name_technical': 'section_font',
                    'type': 'options',
                    'preview_img': 'font.png',
                    'option_field_ids': [
                        (0, 0, {'field_type': 'range', 'name_technical': 'font_size', 'name': 'Font Size', 'value_range': 16, 'options': {'range_start': 10, 'range_end': 29}}),
                        (0, 0, {'field_type': 'combo_box', 'name_technical': 'font_family', 'key_combo_box': 'report_utils__font_family', 'name': 'Font Family', 'value_combo_box': False}),
                        (0, 0, {'field_type': 'combo_box', 'name_technical': 'font_family2', 'key_combo_box': 'report_utils__font_family', 'name': 'Font Family (Secondary Lang)', 'value_combo_box': False}),
                        (0, 0, {'field_type': 'range', 'name_technical': 'font_line_height', 'name': 'Font Line Height', 'value_range': False, 'options': {'range_start': 8, 'range_end': 20}}),
                    ]
                    }
        elif name == "section_custom_color":
            return {'name': 'Custom Color',
                    'name_technical': 'section_custom_color',
                    'type': 'options',
                    'preview_img': 'color.png',
                    'option_field_ids': [
                        (0, 0, {'field_type': 'boolean', 'name_technical': 'apply_custom_color', 'name': 'Apply Custom Color', 'value_boolean': False}),
                        (0, 0, {'field_type': 'color', 'name_technical': 'custom_color1', 'name': 'Primary Color', 'value_color': '#344c67'}),
                        (0, 0, {'field_type': 'color', 'name_technical': 'custom_color2', 'name': 'Secondary Color', 'value_color': '#aabed4'}),
                        (0, 0, {'field_type': 'color', 'name_technical': 'custom_color_font', 'name': 'Font Color', 'value_color': 'black'}),
                    ]
                    }

        elif name == "section_label":

            option_field_ids = [
                        (0, 0, {'sequence': 1, 'name_technical': 'label_case', 'field_type': 'combo_box', 'key_combo_box': 'report_utils__letter_case', 'name': 'Label Case', 'value_combo_box': 'uppercase', }),
                        (0, 0, {'sequence': 2, 'name_technical': 'label_font_weight', 'field_type': 'combo_box', 'key_combo_box': 'report_utils__font_weight', 'name': 'Label Font Weight', 'value_combo_box': 'bold', }),
                        (0, 0, {'sequence': 3, 'name_technical': 'label_record_reference', 'field_type': 'text', 'value_text': 'No:', 'name': 'Label Record Reference'}),
            ] + additional

            set_sequence(option_field_ids)

            return {'name': 'Label',
                    'name_technical': 'section_label',
                    'type': 'options',
                    'preview_img': 'label.png',
                    'option_field_ids': option_field_ids
         }

        elif name == "section_translate":
            return {'name': 'Translated Terms',
                    'name_technical': 'section_translate',
                    'type': 'translate_terms',
                    'preview_img': 'translate.png',
                    'translate_term_ids': [
                    ],
                    }

        raise NotImplementedError()

    def check_config(self):

        for line in self.line_ids:

            # Row Column width check
            if sum([r.width for r in line.row_ids]) > 100:
                raise UserError(f"The sum of the width values has exceeded 100%. ({line.name})")

            # Secondary Language Module Installation
            for l in line.row_ids:
                if l.type_id.name_technical == "address_lang2" and not self.multi_language:
                    raise UserError(f'You have selected the second language address.'
                                    f'But you didn\'t activate multi language in report.')

                if l.type_id.name_technical == "address_lang2" and not self.check_installed('partner_address_language_secondary'):
                    raise UserError(f'You have selected the second language address in \'{self.second_lang_id.name or "Unknown"}\' language.'
                                    f' But you have to install \'Address Secondary Language\' module.\n'
                                    f'Download Link: '
                                    f'https://apps.odoo.com/apps/modules/16.0/partner_address_language_secondary/')

    def write(self, vals):
        res = super(ReportTemplate, self).write(vals)
        for rec in self:
            rec.check_config()
        return res

    def t_add_element(self, t, key, value):
        class Obj:
            pass

        current_obj = t
        count = 0
        for e in key.split("."):
            count += 1

            if count == len(key.split(".")):
                setattr(current_obj, e, value)
            elif not hasattr(current_obj, e):
                setattr(current_obj, e, Obj)

            current_obj = getattr(current_obj, e)

    def set_data(self, data):
        self.ensure_one()

        class Template:
            pass

        class BreaksTemplate:
            pass
    
        class FontTemplate:
            pass

        t = Template()
        # breaks = BreaksTemplate()
        # font_css = FontTemplate()

        # Set Attributes
        for field in self.env.ref('report_utils.model_report_template').field_id:
            setattr(t, field.name, getattr(self, field.name))

        # Set Methods
        # todo remove unused methods below
        t.pixel_to_break = self.pixel_to_break
        t.get_fields_ids_data = self.get_fields_ids_data
        t.check_installed = self.check_installed
        t.merge_css = self.merge_css
        # t.get_line_display_type = self.get_line_display_type
        t.newline_to_br = self.newline_to_br
        t.get_signature_data = self.get_signature_data
        t.to_pixel = self.to_pixel
        t.find_percent = self.find_percent
        t.from_pixel = self.from_pixel
        t.html_to_text = self.html_to_text
        t._hasattr = self._hasattr

        def multi_lang_html(lang1, lang2, separator='<br/>', tag="span", style="", show_value=None, value=None, value_prefix=None, lang2_tag_style=""):
            result = f'<{tag} style="{style}">{lang1}</{tag}>\n'
            if self.multi_language and lang2:
                result += f'{separator}\n'
                standard_font_lang2 = data['standard_font_lang2']
                result += f'<{tag} style="{standard_font_lang2};{style};{lang2_tag_style}">{lang2}</{tag}>\n'

            if show_value:
                if value_prefix:
                    result += value_prefix
                result += value or ""

            return result

        def format_lines(objects, name_technical, order=None, image_attribute="product_id.image_1920"):
            if order:
                objects = objects.sorted(key=lambda x: getattr(x, order))
            elif objects and hasattr(objects[0], 'sequence'):
                objects = objects.sorted(key=lambda x: x.sequence)

            line_data = self.get_fields_ids_data(objects, name_technical)
            th_style = self.merge_css(data['standard_font'], data['label_style'], data['lines_header_style'], 'padding:4px;text-align:center')
            td_style = self.merge_css(data['standard_font'], 'border:1px solid '+ data['parameters'].color1, 'padding:4px;border-style: solid')
            tr_list = []
            th_list = []

            # Header
            count = 0
            if data.get('show_serial_number'):
                # count += 1
                th_list.append(f"""<th style="{th_style}">{multi_lang_html(data['serial_number_heading'], data['serial_number_heading_lang2'])}</th>""")
            for line in line_data['header']:
                count += 1
                if data.get('show_product_image') and count == data['product_image_position']:
                    th_list.append(f"""<th style="{th_style}">{multi_lang_html(data['product_image_column_heading'], data['product_image_column_heading_lang2'])}</th>""")

                if not line['invisible']:
                    th_list.append(f"""<td style="{th_style};{line['width_style']}">{multi_lang_html(line['label'], line['label_lang2'])}</th>""")

            tr_list.append("<tr>%s</tr>" % "".join(th_list))

            # Content
            tr_count = 0
            for line in line_data['content']:
                display_type = self.get_line_display_type(line)
                display_type_value = self.get_line_display_type(line, return_value=True)

                tr_count += 1
                td_list = []
                td_count = 0

                if not display_type or display_type == 'product':
                    if data.get('show_serial_number'):
                        # td_count += 1
                        td_list.append(f"""<td style="{td_style};text-align:center">{tr_count}</th>""")

                    for line_td in line:

                        td_count += 1
                        if data.get('show_product_image') and td_count == data['product_image_position']:
                            image_data = getattr_new(line_td['line_id'], image_attribute)
                            product_img = f"""<img style="width:{data['product_image_width']}px" src="{image_data_uri(image_data)}"/>""" if image_data else ""
                            td_list.append(f"""<td style="{td_style};">{product_img}</th>""")

                        if not line_td['invisible']:
                            td_list.append(f"""<td style="{td_style};{line_td['alignment_style']}">{line_td['value']}</td>""")
                
                elif display_type == 'line_section':
                    td_list.append(f"""<td colspan="99" style="{td_style}">{display_type_value}</td>""")

                elif display_type == 'line_note':
                    td_list.append(f"""<td colspan="99" style="{td_style};font-style:italic">{self.newline_to_br(display_type_value)}</td>""")

                tr_list.append("<tr>%s</tr>" % "".join(td_list))

            result = f"""
            <table style="width:100%;{data['standard_font']};border-style: solid;">
                { "".join(tr_list)}
            </table>
            """

            return result

        def format_amount(obj, name_technical):
            amount_data = self.get_fields_ids_data(obj, name_technical)['content'][0]

            amount_in_text_html = ""
            if data['show_amount_in_text']:
                amount_in_text_html = f"""
                <p style="padding:4px">
                    {data['label_amount_in_text']}:<br/>{self.get_amount_in_text(obj, 'amount_total')}
                </p>
                """

            tr_list = []
            count = 0
            for line in amount_data:
                count += 1
                td_list = []
                if count == 1:
                    td_list += f"""<td rowspan="{len(amount_data)}" style="width:60%;vertical-align:bottom;text-align:center;font-size:{self.to_pixel(self.find_percent(self.from_pixel(data['font']['font-size']), percent=90))};border-right:1px solid {data['parameters'].color1};border-top:0px solid transparent">{amount_in_text_html}</td>"""
                
                min_width = f"min-width:{len(line['label'] + (line['label_lang2'] or '')) * 9}px"

                td_list += [
                    f"""<td style="text-align:right;padding:4px;{data['lines_header_style']};border-right:0px solid transparent;border-top:0px solid transparent;{min_width}">{multi_lang_html(line['label'], line['label_lang2'], separator=" ")}</td>""",
                    f"""<td style="text-align:center;padding:4px;{data['lines_header_style']};border-left:0px solid transparent;border-top:0px solid transparent">:</td>""",
                    f"""<td style="text-align:right;padding:4px;{data['lines_header_style']};border-top:0px solid transparent;min-width:100px">{line['value']}</td>"""
                ]

                tr_list.append("<tr>%s</tr>" % "".join(td_list))

            return "".join(tr_list)

        def format_signature_boxes(name_technical='section_signature_box'):
            signature_data = self.get_signature_data(name_technical)

            if not signature_data:
                return ""

            result = "<br/>"
            
            td_list = []
            for sign_box in signature_data.sorted(key=lambda x: x.sequence):
                td_list.append(f"""<td style="border:1px solid {data['parameters'].color1};font-weight:bold;text-align:center;padding:4px;">{multi_lang_html(lang1=sign_box.heading, lang2=sign_box.heading_lang2)}</td>""")
            result += f"<tr>{''.join(td_list)}</tr>"

            td_list = []
            for sign_box in signature_data:
                td_list.append(f"""<td style="border:1px solid {data['parameters'].color1};border-top:0px;height:130px"/>""")
            result += f"<tr>{''.join(td_list)}</tr>"

            return f"""<table style="width:100%;{data['standard_font']};border-style: solid;">{result}</table>"""

        def format_address(obj, name_technical):
            result = ""
            for line in self.get_fields_ids_data(obj, name_technical)['content'][0]:
                if line['value'] and line['separator']:
                    result += f'<span>{line["separator"]}</span>'
                if line['label']:
                    result += f'<span>{line["label"]}</span><span>:</span>'
                if line['value']:
                    result += f'<span>{line["value"]}</span>'
            return result
        
        def check_visibility_condition(expression, obj):
            if expression and expression.strip():
                try:
                    return safe_eval(expression, {'record': obj})
                except Exception as e:
                    raise UserError(f"Error:{e} Expression:{expression}")
            return True

        def format_other_fields_td(obj, name_technical):
            td1 = []
            td2 = []
            count = 0
            for line in self.get_fields_ids_data(obj, name_technical)['content'][0]:
                visibility_condition = check_visibility_condition(expression=line['visibility_condition'], obj=obj)

                if (line['value'] or line['null_value_display']) and visibility_condition:
                    count += 1
                    td = td1 if count % 2 == 1 else td2
                    label_result = multi_lang_html(line['label'], line['label_lang2'], style=data['label_style'], show_value=True, value=line['value'], value_prefix="<br/>")
                    label_result += "<br/>"
                    td.append(label_result)

            result = f"""
            <td style="vertical-align:top;">{"".join(td1)}</td>
            <td style="vertical-align:top;">{"".join(td2)}</td>
            """
            return result

        self.t_add_element(t=t, key="HtmlBreaks.after_header", value=self.pixel_to_break(data.get('padding_after_header', 0)))
        self.t_add_element(t=t, key="HtmlBreaks.before_lines", value=self.pixel_to_break(data.get('padding_before_lines', 0)))
        self.t_add_element(t=t, key="Font.standard", value=data.get('standard_font'))
        self.t_add_element(t=t, key="Font.standard_lang2", value=data.get('standard_font_lang2'))
        self.t_add_element(t=t, key="Label.font", value=data.get('label_style'))
        self.t_add_element(t=t, key="Label.partner", value=data.get('label_partner') or "")
        self.t_add_element(t=t, key="Label.partner_lang2", value=data.get('label_partner_lang2') or "")

        # Fooooo
        # add_element(key="Label.invoicing_address", value=data.get('label_invoicing_address') or "")
        # add_element(key="Label.shipping_address", value=data.get('label_shipping_address') or "")
        # add_element(key="Label.invoicing_and_shipping_address", value=data.get('label_invoicing_and_shipping_address') or "")
        # add_element(key="Label.invoicing_address_lang2", value=data.get('label_invoicing_address_lang2') or "")
        # add_element(key="Label.shipping_address_lang2", value=data.get('label_shipping_address_lang2') or "")
        # add_element(key="Label.invoicing_and_shipping_address_lang2", value=data.get('label_invoicing_and_shipping_address_lang2') or "")

        self.t_add_element(t=t, key="Label.linesLabel", value=data.get('lines_label') or "")
        self.t_add_element(t=t, key="Label.linesLabel_lang2", value=data.get('lines_label_lang2') or "")
        self.t_add_element(t=t, key="ExtraTerms.show_in_next_page", value=data.get('show_extra_terms_next_page'))
        self.t_add_element(t=t, key="ExtraTerms.value", value=data.get('extra_terms'))
        self.t_add_element(t=t, key="Header.show", value=data.get('show_header'))
        self.t_add_element(t=t, key="Footer.show", value=data.get('show_footer'))
        self.t_add_element(t=t, key="Footer.image", value=data.get('footer_image'))
        self.t_add_element(t=t, key="Header.image", value=data.get('header_image'))
        self.t_add_element(t=t, key="Footer.show_border_line", value=data.get('show_footer_border_line'))
        self.t_add_element(t=t, key="Header.layout", value=data.get('header_layout'))
        self.t_add_element(t=t, key="Footer.layout", value=data.get('footer_layout'))
        self.t_add_element(t=t, key="Logo.style", value=data.get('logo_style'))
        self.t_add_element(t=t, key="Logo.image", value=data.get('logo_image'))
        self.t_add_element(t=t, key="Logo.show", value=data.get('show_logo'))
        self.t_add_element(t=t, key="Header.reference_number", value=data.get('reference_number'))
        self.t_add_element(t=t, key="Header.style", value=data.get('header_style'))
        self.t_add_element(t=t, key="Footer.style", value=data.get('footer_style'))
        self.t_add_element(t=t, key="Header.heading", value=data.get('heading_name'))
        self.t_add_element(t=t, key="Font.size", value=data['font']['font-size'])
        self.t_add_element(t=t, key="Header.show_border_line", value=data.get('show_header_border_line'))
        self.t_add_element(t=t, key="Parameters", value=data.get('parameters'))
        self.t_add_element(t=t, key="ReportTime.show", value=data.get('show_print_time'))

        self.t_add_element(t=t, key="MultiLangHtml", value=multi_lang_html)
        self.t_add_element(t=t, key="Label.style", value=data['label_style'])
        self.t_add_element(t=t, key="FormatAddress", value=format_address)
        self.t_add_element(t=t, key="FormatOtherFieldsTd", value=format_other_fields_td)
        self.t_add_element(t=t, key="FormatLines", value=format_lines)
        self.t_add_element(t=t, key="FormatAmount", value=format_amount)
        self.t_add_element(t=t, key="FormatSignatureBoxes", value=format_signature_boxes)

        t.data = data
        return t

