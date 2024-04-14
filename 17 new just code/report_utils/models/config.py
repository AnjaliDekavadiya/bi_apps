# -*- coding: utf-8 -*-
from base64 import b64decode
from io import BytesIO
import ast
from logging import getLogger
logger = getLogger(__name__)

from odoo import api, fields, models
from odoo.exceptions import UserError
from PIL import Image
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from PyPDF2.utils import PdfReadError
except ImportError:
    logger.debug("Can not import PyPDF2")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def open_custom_template(self):

        report_name = self._context['report_name']
        company_id = False
        template_obj = self.env['report.template']
        report_list = template_obj.get_report_list()
        multi_company_applicable = report_list.get(report_name) and report_list.get(report_name).get('multi_company_applicable')

        if multi_company_applicable:
            company_id = self.company_id

        report_id = template_obj.get_template(report_name, company_id=company_id)

        if not report_id:
            if report_name not in report_list:
                raise UserError('We couldn\'t find report \'%s\'' % report_name)

            template_obj.reset_template(report_name, company_id=company_id)
            report_id = template_obj.get_template(report_name, company_id=company_id)


        return {
            'name': 'Configure Report',
            'type': 'ir.actions.act_window',
            'res_model': 'report.template',
            'view_mode': 'form',
            'res_id': report_id.id,
            'views': [[False, 'form']],
        }


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    
    @api.model
    def _run_wkhtmltopdf(self, bodies, report_ref=False, header=None, footer=None, landscape=False, specific_paperformat_args=None, set_viewport_size=False):
        res = super(IrActionsReport, self)._run_wkhtmltopdf(bodies=bodies, report_ref=report_ref, header=header, footer=footer, landscape=landscape, specific_paperformat_args=specific_paperformat_args, set_viewport_size=set_viewport_size)

        data = self.env['report.template'].get_watermark_pdf(report_ref)
        if not data:
            return res

        report_name, option = data.split(',')
        t = self.env['report.template'].search([('name', '=', report_name)])

        if not t:  # Otherwise error will come directly print report without configuration created
            return res

        b64_data = getattr(t, 'get_option_data')(option)

        if not b64_data:
            return res

        try:
            pdf_watermark = PdfFileReader(BytesIO(b64decode(b64_data)))
        except:
            pdf_watermark = None

        if not pdf_watermark:
            return res

        pdf = PdfFileWriter()
        for page in PdfFileReader(BytesIO(res)).pages:
            watermark_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            # print(page.mediaBox.getWidth())
            # print(page.mediaBox.getHeight())
            # print(pdf_watermark.getPage(0).mediaBox.getHeight())
            # print(pdf_watermark.getPage(0).mediaBox.getHeight())

            # main_width, main_height = page.mediaBox.upperRight
            # width, height = pdf_watermark.getPage(0).mediaBox.upperRight
            #
            #
            #
            # scale = min(main_width / width, main_height / height)
            # pdf_watermark.getPage(0).scaleTo(main_width * scale, main_height * scale)
            # pdf_watermark.getPage(0).scaleTo(page.mediaBox.getHeight(), page.mediaBox.getWidth())
            # print(main_width)
            # print(main_height)
            # print(width)
            # print(height)



            watermark_page.mergePage(pdf_watermark.getPage(0))
            watermark_page.mergePage(page)

        pdf_content = BytesIO()
        pdf.write(pdf_content)
        return pdf_content.getvalue()


