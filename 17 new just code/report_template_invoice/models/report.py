# # -*- coding: utf-8 -*-
from odoo import models


class ReportCustomTemplate(models.Model):
    _inherit = 'report.template'

    def list_multi_language_options(self):
        res = super(ReportCustomTemplate, self).list_multi_language_options()
        res['report_customer_invoice'] = self.get_standard_multi_language_options()
        return res

    # def is_report_customer_invoice(self):
    #     return bool(self.name == "report_customer_invoice")

    def get_report_list(self):
        res = super(ReportCustomTemplate, self).get_report_list()
        options_separator = (0, 0, {'field_type': 'break', 'name_technical': '-1', 'name': '-', })

        res["report_customer_invoice"] = {
            'name_display': 'Customer Invoice Template',
            'paperformat_id': self.env.ref("report_template_invoice.paperformat_invoice_euro_fit").id,
            'multi_company_applicable': True,
            'lines': [
                self.get_standard_report_line("section_general"),
                self.get_standard_report_line("section_header_layout"),
                self.get_standard_report_line("section_footer_layout"),
                self.get_standard_report_line("section_header_address"),
                self.get_standard_report_line("section_header_address_lang2"),
                self.get_standard_report_line("section_footer"),
                self.get_standard_report_line("section_header_footer_images"),
                self.get_standard_report_line("section_header_footer_layout"),
                self.get_standard_report_line("section_partner_address"),

                {'name': 'Other Fields',
                 'name_technical': 'section_other_fields',
                 'model_id': 'account.move',
                 'type': 'fields',
                 'preview_img': '2_right.png',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'field_id': 'invoice_date', 'label': 'Invoice Date', 'null_value_display': False}),
                     (0, 0, {'sequence': 10, 'field_id': 'invoice_date_due', 'label': 'Due Date', 'null_value_display': False}),
                     (0, 0, {'sequence': 10, 'field_id': 'invoice_origin', 'label': 'Source', 'null_value_display': False}),
                     (0, 0, {'sequence': 10, 'field_id': 'partner_id', 'label': 'Customer Code', 'null_value_display': False, 'field_display_field_id': 'ref'}),
                     (0, 0, {'sequence': 10, 'field_id': 'ref', 'label': 'Ref', 'null_value_display': False}),
                 ],
                 },

                {'name': 'Invoice Lines',
                 'name_technical': 'section_lines',
                 'model_id': 'account.move.line',
                 'type': 'lines',
                 'preview_img': '3_lines.png',
                 'data_field_names': 'display_type',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'alignment': 'left', 'field_id': 'name', 'label': 'Description'}),
                     (0, 0, {'sequence': 20, 'alignment': 'center', 'field_id': 'quantity', 'label': 'Quantity'}),
                     (0, 0, {'sequence': 30, 'alignment': 'right', 'field_id': 'price_unit', 'label': 'Unit Price', 'width': '12%'}),
                     (0, 0, {'sequence': 40, 'alignment': 'center', 'field_id': 'product_uom_id', 'label': 'UOM'}),
                     (0, 0, {'sequence': 50, 'alignment': 'right', 'field_id': 'discount', 'label': 'Disc.%', 'null_hide_column': True}),
                     (0, 0, {'sequence': 60, 'alignment': 'center', 'field_id': 'tax_ids', 'label': 'Taxes', 'width': '10%'}),
                     (0, 0, {'sequence': 70, 'alignment': 'right', 'field_id': 'price_subtotal', 'label': 'Amount', 'currency_field_expression': 'move_id.currency_id', 'thousands_separator': 'applicable', 'width': '12%'}),
                 ],
                 },

                {'name': 'Invoice Lines Advanced',
                 'name_technical': 'section_lines_advanced',
                 'type': 'options',
                 'preview_img': '3_lines.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'char', 'name_technical': 'lines_label', 'name': 'Label For Lines', 'value_char': 'Product Items'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'lines_label_lang2', 'name': 'Label For Lines (Secondary Lang)', 'value_char': ''}),
                     options_separator,
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_serial_number', 'name': 'Show serial number ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'serial_number_heading', 'name': 'Serial number heading', 'value_char': 'Sl.'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'serial_number_heading_lang2', 'name': 'Serial number heading (Secondary Lang)', 'value_char': ''}),
                     options_separator,
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_product_image', 'name': 'Show product image ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'range', 'name_technical': 'product_image_position', 'name': 'Product image position (Column Number)', 'value_range': 1, 'options': {'range_start': 1, 'range_end': 10}}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'product_image_column_heading', 'name': 'Product image heading', 'value_char': 'Image'}),
                     (0, 0, {'field_type': 'char', 'name_technical': 'product_image_column_heading_lang2', 'name': 'Product image heading (Secondary Lang)', 'value_char': ''}),
                     (0, 0, {'field_type': 'range', 'name_technical': 'product_image_width', 'name': 'Product image width (Pixels)', 'value_range': 75, 'options': {'range_start': 50, 'range_end': 100}}),]
                 },

                {'name': 'Amount',
                 'name_technical': 'section_amount',
                 'model_id': 'account.move',
                 'type': 'fields',
                 'preview_img': '4_bottom_right.png',
                 'field_ids': [
                     (0, 0, {'sequence': 10, 'thousands_separator': 'applicable', 'field_id': 'amount_untaxed', 'label': 'Untaxed Amount'}),
                     (0, 0, {'sequence': 20, 'thousands_separator': 'applicable', 'field_id': 'amount_tax', 'label': 'Tax'}),
                     (0, 0, {'sequence': 30, 'thousands_separator': 'applicable', 'field_id': 'amount_total', 'label': 'Amount With Tax'}),
                 ],
                 },
                self.get_standard_report_line("section_amount_in_words"),

                {'name': 'Report Headings',
                 'name_technical': 'section_heading',
                 'type': 'options',
                 'preview_img': '2_top.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'text', 'name_technical': 'state_posted', 'name': 'HEADING:IF STATE IS POSTED', 'value_text': 'SALES\nINVOICE'}),
                     (0, 0, {'field_type': 'text', 'name_technical': 'state_draft', 'name': 'HEADING:IF STATE IS DRAFT', 'value_text': 'DRAFT\nINVOICE'}),
                     (0, 0, {'field_type': 'text', 'name_technical': 'state_cancel', 'name': 'HEADING:IF STATE IS CANCELLED', 'value_text': 'CANCELLED\nINVOICE'}),
                ]
                 },

                {'name': 'Signature Boxes',
                 'name_technical': 'section_signature_box',
                 'type': 'signature_boxes',
                 'preview_img': '4_bottom_left_right.png',
                 'note': '<p class="text-muted">If you don\'t need signature box, please delete all lines</p>',
                 'signature_box_ids': [
                     (0, 0, {'heading': 'Authorized Signature'}),
                     (0, 0, {'heading': 'Customer Signature'}),
                 ],
                 },

                {'name': 'Breaks',
                 'name_technical': 'section_breaks',
                 'type': 'options',
                 'preview_img': 'break.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'range', 'name_technical': 'padding_after_header', 'name': 'Padding after Header (Pixel)', 'value_range': 16, 'options': {'range_start': 0, 'range_end': 50}}),
                     (0, 0, {'field_type': 'range', 'name_technical': 'padding_before_lines', 'name': 'Padding before Lines (Pixel)', 'value_range': 16, 'options': {'range_start': 0, 'range_end': 50}}),
                 ]
                 },

                self.get_standard_report_line("section_watermark"),
                self.get_standard_report_line("section_logo"),
                self.get_standard_report_line("section_font"),
                self.get_standard_report_line("section_custom_color"),
                self.get_standard_report_line("section_label", additional=[
                    (0, 0, {'name_technical': 'label_partner_lang2', 'field_type': 'char', 'name': 'LABEL: Customer (Secondary Lang)', 'value_char': ''}),
                    (0, 0, {'name_technical': 'label_partner', 'field_type': 'char', 'name': 'LABEL: Customer', 'value_char': 'Customer'}),
                ]),
                self.get_standard_report_line("section_translate"),

                {'name': 'Other Options',
                 'name_technical': 'section_other_options',
                 'type': 'options',
                 'preview_img': 'other.png',
                 'option_field_ids': [
                     (0, 0, {'field_type': 'timezone', 'name_technical': 'report_timezone', 'name': 'Report Timezone'}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_note', 'name': 'Show Terms & Conditions ?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_payment_communication', 'name': 'Show Payment Communication Line?', 'value_boolean': True}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_print_time', 'name': 'Show Time in the print ?', 'value_boolean': False}),
                     (0, 0, {'field_type': 'html', 'name_technical': 'extra_terms', 'name': 'Extra Terms & Conditions'}),
                     (0, 0, {'field_type': 'boolean', 'name_technical': 'show_extra_terms_next_page', 'name': 'Show Extra Terms & Conditions in Next Page ?', 'value_boolean': False}),

                     (0, 0, {'field_type': 'combo_box', 'name_technical': 'direction', 'key_combo_box': 'report_utils__direction', 'name': 'Direction', 'value_combo_box': 'LTR', }),
                 ]
                 },
            ],
        }
        return res

    def get_watermark_pdf_list(self):
        res = super(ReportCustomTemplate, self).get_watermark_pdf_list()

        res["account.report_invoice_with_payments"] = "report_customer_invoice,watermark_pdf"
        res["account.report_invoice"] = "report_customer_invoice,watermark_pdf"

        return res

