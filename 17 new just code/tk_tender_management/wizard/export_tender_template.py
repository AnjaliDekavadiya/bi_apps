# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import xlwt
import base64
import logging
import tempfile
import binascii
import xlrd
from xlrd.timemachine import xrange
from odoo import fields, api, models
from odoo.exceptions import ValidationError
from io import BytesIO


class ExportTenderLine(models.TransientModel):
    _name = 'export.tender.line'
    _description = "Export Tender Line"

    name = fields.Char(string="Product ")
    product_ids = fields.Many2many('product.product', domain="[('default_code','!=',False)]")

    def action_export_tender_line(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        heading = xlwt.easyxf("align: vert centre, horiz centre;font: bold on,height 200")
        sheet_style = xlwt.easyxf("align: vert centre, horiz centre")
        sheet1 = workbook.add_sheet('Product', cell_overwrite_ok=True)
        sheet1.write(0, 0, 'Product', heading)
        sheet1.write(0, 1, 'Code', heading)
        sheet1.write(0, 2, 'Description', heading)
        sheet1.write(0, 3, 'Unit of Measure', heading)
        sheet1.write(0, 4, 'Quantity', heading)
        c = 1
        product = self.env['product.product'].browse(self.product_ids.ids)
        for data in product:
            sheet1.write(c, 0, data.name, sheet_style)
            sheet1.write(c, 1, data.default_code, sheet_style)
            sheet1.write(c, 2, data.name, sheet_style)
            sheet1.write(c, 3, data.uom_id.name)
            sheet1.write(c, 4, 1)

            c = c + 1
        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())
        attachment = self.env['ir.attachment'].sudo()
        filename = "tender_product" + ".xls"
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'datas': out})
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment_id.id),
                'target': 'self',
                'nodestroy': False,
            }
            return report


class ImportTenderLine(models.TransientModel):
    _name = 'import.tender.line'
    _description = "Import Tender Line"

    file = fields.Binary('File')
    file_name = fields.Char("File Name", help="File Name")
    from_bidding = fields.Boolean(string="From Bidding")

    def import_line_from_file(self):
        if not self.from_bidding:
            active_id = self._context.get('active_id')
            tender_line = self.env['tender.info.line'].sudo()
            if not self.file:
                return
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            # read header values into the list
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            start_range = 1
            lines = []
            for row_index in xrange(start_range, sheet.nrows):
                raw_data = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in
                            xrange(sheet.ncols)}
                lines.append(raw_data)
            for raw_data in lines:
                try:
                    product_id = self.env['product.product'].search([('default_code', '=', raw_data.get('Code'))])
                    if product_id:
                        data = {
                            'product_id': product_id.id,
                            'name': raw_data.get('Description'),
                            'qty': int(raw_data.get('Quantity')),
                            'tender_id': active_id
                        }
                        tender_line.create(data)
                except Exception as e:
                    raise ValidationError(e)
        if self.from_bidding:
            bidding_id = self._context.get('active_id')
            bidding_line = self.env['tender.bidding.line'].sudo()
            if not self.file:
                return
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            # read header values into the list
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            start_range = 1
            lines = []
            for row_index in xrange(start_range, sheet.nrows):
                raw_data = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in
                            xrange(sheet.ncols)}
                lines.append(raw_data)
            for raw_data in lines:
                try:
                    tender_bidding_id = self.env['tender.bidding'].browse(bidding_id)
                    product_id = self.env['product.product'].search([('default_code', '=', raw_data.get('Code'))])
                    for data in tender_bidding_id.bidding_line_ids:
                        if data.product_id.id == product_id.id and not data.display_type:
                            data.write({
                                'price': float(raw_data.get('Your Price / Qty.'))
                            })
                    tender_bidding_id._compute_bid_total()
                except Exception as e:
                    raise ValidationError(e)
