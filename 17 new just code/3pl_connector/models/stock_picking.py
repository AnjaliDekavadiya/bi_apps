# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter
import tempfile
import xlrd
import csv
import re
import os
# from bs4 import BeautifulSoup
from odoo.tools import html2plaintext
# import html2text as html2plaintext


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_exported = fields.Boolean("Exported", default=False, copy=False, help="True if picking is exported to 3PL.")
    tpl_status = fields.Char("Status", copy=False, default="-", help="3PL Status.")

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        context = dict(self.env.context or {})
        # domain = []
        default_warehouse_id = context.get("default_warehouse_id")
        picking_type_id = self.env["stock.picking.type"].sudo().search([('warehouse_id', '=', default_warehouse_id)])
        if default_warehouse_id and picking_type_id:
            domain.append(('picking_type_id', 'in', picking_type_id.ids))
        return super(StockPicking, self)._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        domain = domain or []
        context = dict(self.env.context or {})
        default_warehouse_id = context.get("default_warehouse_id")
        picking_type_id = self.env["stock.picking.type"].sudo().search([('warehouse_id', '=', default_warehouse_id)])
        if default_warehouse_id and picking_type_id:
            domain.append(('picking_type_id', 'in', picking_type_id.ids))
        return super(StockPicking, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order="write_date asc", **read_kwargs)

    def create_so_excel_file_for_3pl(self, warehouse, process_log):
        try:
            process_log_line_obj = self.env["process.log.line"]
            if not self:
                raise UserError(_("Data not available for export pickings. Select at least 1 picking to export."))
            temp_location = tempfile.mkstemp()[1]
            workbook = xlsxwriter.Workbook(temp_location + '.xlsx')

            cell_data_format = workbook.add_format({
                'align': 'left', 'border': 1, 'size': 10})
            cell_amount_format = workbook.add_format({
                'align': 'right', 'border': 1, 'size': 10})
            try:
                worksheet = workbook.add_worksheet("product")
                row, column = 0, 0
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 25)
                worksheet.set_column('D:D', 25)
                worksheet.set_column('E:E', 15)
                worksheet.set_column('F:F', 15)
                worksheet.set_column('G:G', 25)
                worksheet.set_column('H:H', 25)
                worksheet.set_column('I:I', 10)
                worksheet.set_column('J:J', 10)
                worksheet.set_column('K:K', 15)
                worksheet.set_column('L:L', 15)
                worksheet.set_column('M:M', 15)
                worksheet.set_column('N:N', 15)
                worksheet.set_column('O:O', 15)
                worksheet.set_column('P:P', 15)
                worksheet.set_column('Q:Q', 15)
                worksheet.set_column('R:R', 15)
                worksheet.set_column('S:S', 15)
                worksheet.set_column('T:T', 15)
                worksheet.set_column('U:U', 15)
                worksheet.set_column('U:U', 15)

                # Report Headers
                worksheet.write(row, 0, 'Picking Ref.', cell_data_format)
                worksheet.write(row, 1, 'Source Document', cell_data_format)
                worksheet.write(row, 2, 'Tracking reference', cell_data_format)
                worksheet.write(row, 3, 'Tracking link', cell_data_format)
                worksheet.write(row, 4, 'Product Internal Reference', cell_data_format)
                worksheet.write(row, 5, 'Product Name', cell_data_format)
                worksheet.write(row, 6, 'Product Barcode', cell_data_format)
                worksheet.write(row, 7, 'Quantity', cell_data_format)
                worksheet.write(row, 8, 'Delivery Name', cell_data_format)
                worksheet.write(row, 9, 'Company Name', cell_data_format)
                worksheet.write(row, 10, 'Delivery Street', cell_data_format)
                worksheet.write(row, 11, 'Delivery Street2', cell_data_format)
                worksheet.write(row, 12, 'Delivery City', cell_data_format)
                worksheet.write(row, 13, 'Delivery Zip', cell_data_format)
                worksheet.write(row, 14, 'Delivery State', cell_data_format)
                worksheet.write(row, 15, 'Delivery Country', cell_data_format)
                worksheet.write(row, 16, 'Delivery Email', cell_data_format)
                worksheet.write(row, 17, 'Delivery Mobile', cell_data_format)
                worksheet.write(row, 18, 'Note', cell_data_format)
                worksheet.write(row, 19, 'Lot/Serial Number', cell_data_format)
                worksheet.write(row, 20, 'Done Quantity', cell_data_format)
                worksheet.write(row, 21, 'Status', cell_data_format)
                row += 1
                for move in self.mapped("move_ids_without_package"):
                    try:
                        line_skipped = True
                        process_log_line_vals = {
                            "process_log_id": process_log.id,
                            "product_id": move.product_id.id,
                            "picking_id": move.picking_id.id,
                            "is_mismatch": False,
                            "message": "Line Exported Successfully For Picking %s , Product %s" % (move.picking_id.name, move.product_id.display_name)
                        }
                        process_log_line = process_log_line_obj.create(process_log_line_vals)
                        for rec in move:
                            if rec.picking_id.state == 'draft':
                                status = "Draft"
                            elif rec.picking_id.state == 'waiting':
                                status = "Waiting Another Operation"
                            elif rec.picking_id.state == 'confirmed':
                                status = "Waiting"
                            elif rec.picking_id.state == 'assigned':
                                status = "Ready"
                            elif rec.picking_id.state == 'done':
                                status = "Done"
                            elif rec.picking_id.state == 'cancel':
                                status = "Cancelled"
                            else:
                                status = " - "

                        lot_number = ''
                        for move_line in move.move_line_ids:
                            if move.product_id and move.product_id.tracking == 'lot':
                                lot_number = move_line.lot_id.name or ''
                            elif move.product_id and move.product_id.tracking == "serial":
                                if move_line.lot_id.name:
                                    lot_number += move_line.lot_id.name + ","
                        lot_number = lot_number.rstrip(',')
                        text_note = ''
                        if move.picking_id.note:
                            text_note = html2plaintext(move.picking_id.note)
                        # text_note = excel_note.get_text()
                        # Product Details
                        worksheet.write(row, 0, move.picking_id.name, cell_data_format)
                        worksheet.write(row, 1, move.picking_id.origin or '', cell_data_format)
                        worksheet.write(row, 2, move.picking_id.carrier_tracking_ref or '', cell_data_format)
                        worksheet.write(row, 3, move.picking_id.carrier_tracking_url or '', cell_data_format)
                        worksheet.write(row, 4, move.product_id.default_code or '', cell_data_format)
                        worksheet.write(row, 5, move.product_id.display_name or '', cell_data_format)
                        worksheet.write(row, 6, move.product_id.barcode or '', cell_amount_format)
                        worksheet.write(row, 7, move.product_uom_qty or '', cell_amount_format)
                        worksheet.write(row, 8, move.picking_id.partner_id.name or '', cell_amount_format)
                        worksheet.write(row, 9, move.picking_id.partner_id.parent_id.name or '', cell_amount_format)
                        worksheet.write(row, 10, move.picking_id.partner_id.street or '', cell_amount_format)
                        worksheet.write(row, 11, move.picking_id.partner_id.street2 or '', cell_data_format)
                        worksheet.write(row, 12, move.picking_id.partner_id.city or '', cell_data_format)
                        worksheet.write(row, 13, move.picking_id.partner_id.zip or '', cell_data_format)
                        worksheet.write(row, 14, move.picking_id.partner_id.state_id.name or '', cell_data_format)
                        worksheet.write(row, 15, move.picking_id.partner_id.country_id.name or '', cell_data_format)
                        worksheet.write(row, 16, move.picking_id.partner_id.email or '', cell_data_format)
                        worksheet.write(row, 17, move.picking_id.partner_id.mobile or '', cell_data_format)
                        worksheet.write(row, 18, text_note or '', cell_data_format)
                        worksheet.write(row, 19, lot_number or '', cell_data_format)
                        worksheet.write(row, 20, move.quantity or '', cell_data_format)
                        worksheet.write(row, 21, status or '', cell_data_format)

                        row += 1
                        line_skipped = False
                        move.is_exported = True
                        if move.picking_id.move_ids_without_package.mapped("is_exported"):
                            move.picking_id.is_exported = True

                        process_log_line.write({
                            "exported_qty": move.product_uom_qty,
                            "file_qty": move.product_uom_qty
                        })

                    except Exception as e:
                        message = "Facing issue while exporting sales pickings : %s" % e
                        process_log_line.write({
                            "message": message,
                            "is_mismatch": True,
                            "is_skip_line": line_skipped
                        })
                        continue

            except Exception as e:
                process_log.note = "Facing issue in export sales process : %s" % e
            workbook.close()

            fp = open(temp_location + '.xlsx', 'rb')
            file_name = '%sexport_%s.xlsx' % (warehouse.export_sales_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
            process_log.file_name = file_name
            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_sales_to.path, file_name)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(fp, dest_path)
                else:
                    sftp_instance.storbinary(f'STOR {file_name}', fp)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export pickings process : %s" % e

            return True
        except Exception as e:
            process_log.note = "Facing issue in export pickings process : %s" % e

    def create_so_csv_file_for_3pl(self, warehouse, process_log):
        file_name = '%sexport_%s.csv' % (warehouse.export_sales_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
        process_log.file_name = file_name
        process_log_line_obj = self.env["process.log.line"]
        with open(file_name, 'w+') as csvfile:
            header_names = [
                "Picking Ref.",
                "Source Document",
                "Tracking reference",
                "Tracking link",
                "Product Internal Reference",
                "Product Name",
                "Product Barcode",
                "Quantity",
                "Delivery Name",
                "Company Name",
                "Delivery Street",
                "Delivery Street2",
                "Delivery City",
                "Delivery Zip",
                "Delivery State",
                "Delivery Country",
                "Delivery Email",
                "Delivery Mobile",
                "Note",
                "Lot/Serial Number",
                "Done Quantity",
                "Status"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=header_names)

            writer.writeheader()
            for move in self.mapped("move_ids_without_package"):
                line_skipped = True
                process_log_line_vals = {
                    "process_log_id": process_log.id,
                    "product_id": move.product_id.id,
                    "picking_id": move.picking_id.id,
                    "is_mismatch": False,
                    "message": "Line Exported Successfully For Picking %s , Product %s" % (move.picking_id.name, move.product_id.display_name)
                }
                text_note = ''
                if move.picking_id.note:
                    text_note = html2plaintext(move.picking_id.note)
                # text_note = excel_note.get_text()
                process_log_line = process_log_line_obj.create(process_log_line_vals)
                for rec in move:
                    if rec.picking_id.state == 'draft':
                        status = "Draft"
                    elif rec.picking_id.state == 'waiting':
                        status = "Waiting Another Operation"
                    elif rec.picking_id.state == 'confirmed':
                        status = "Waiting"
                    elif rec.picking_id.state == 'assigned':
                        status = "Ready"
                    elif rec.picking_id.state == 'done':
                        status = "Done"
                    elif rec.picking_id.state == 'cancel':
                        status = "Cancelled"
                    else:
                        status = " - "

                lot_number = ''
                for move_line in move.move_line_ids:
                    if move.product_id and move.product_id.tracking == 'lot':
                        lot_number = move_line.lot_id.name or ''
                    elif move.product_id and move.product_id.tracking == "serial":
                        if move_line.lot_id.name:
                            lot_number += move_line.lot_id.name + ","
                lot_number = lot_number.rstrip(',')

                try:
                    picking_data = {
                        "Picking Ref.": move.picking_id.name,
                        "Source Document": move.picking_id.origin or '',
                        "Tracking reference": move.picking_id.carrier_tracking_ref or '',
                        "Tracking link": move.picking_id.carrier_tracking_url or '',
                        "Product Internal Reference": move.product_id.default_code or '',
                        "Product Name": move.product_id.display_name or '',
                        "Product Barcode": move.product_id.barcode or '',
                        "Quantity": move.product_uom_qty or '',
                        "Delivery Name": move.picking_id.partner_id.name or '',
                        "Company Name": move.picking_id.partner_id.parent_id.name or '',
                        "Delivery Street": move.picking_id.partner_id.street or '',
                        "Delivery Street2": move.picking_id.partner_id.street2 or '',
                        "Delivery City": move.picking_id.partner_id.city or '',
                        "Delivery Zip": move.picking_id.partner_id.zip or '',
                        "Delivery State": move.picking_id.partner_id.state_id.name or '',
                        "Delivery Country": move.picking_id.partner_id.country_id.name or '',
                        "Delivery Email": move.picking_id.partner_id.email or '',
                        "Delivery Mobile": move.picking_id.partner_id.mobile or '',
                        "Note": text_note or '',
                        "Lot/Serial Number": lot_number or '',
                        "Done Quantity": move.quantity or '',
                        "Status": status
                    }
                    writer.writerow(picking_data)
                    line_skipped = False
                    move.is_exported = True
                    if move.picking_id.move_ids_without_package.mapped("is_exported"):
                        move.picking_id.is_exported = True
                    process_log_line.write({
                        "exported_qty": move.product_uom_qty,
                        "file_qty": move.product_uom_qty
                    })
                except Exception as e:
                    message = "Facing issue while exporting sales pickings : %s" % e
                    process_log_line.write({
                        "message": message,
                        "is_mismatch": True,
                        "is_skip_line": line_skipped
                    })

            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_sales_to.path, file_name)
                csvfile.seek(0)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(csvfile, dest_path)
                else:
                    with open(file_name, 'rb') as csvfile:
                        sftp_instance.storbinary(f'STOR {file_name}', csvfile)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export sales process : %s" % e

            return True

    def export_so_pickings_to_3pl(self, warehouse, process_log):
        pickings = self
        if not pickings:
            picking_domain = [("picking_type_code", "=", "outgoing"),
                              ("is_exported", "=", False),
                              ('picking_type_id.warehouse_id', '=', warehouse.id)]
            if warehouse.last_export_sale_datetime:
                picking_domain.append(("create_date", ">", warehouse.last_export_sale_datetime))
            pickings = self.search(picking_domain)
        if warehouse.export_sales_file_type == "excel":
            pickings.create_so_excel_file_for_3pl(warehouse, process_log)
        else:
            pickings.create_so_csv_file_for_3pl(warehouse, process_log)

        warehouse.last_export_sale_datetime = fields.datetime.now()

        if warehouse.is_notify_users_when_export_sales:
            ctx = dict(self._context)
            ctx.update({
                "email_to": ",".join(warehouse.notify_user_ids_export_sales.mapped("partner_id").mapped("email_formatted")),
                "language": warehouse.notify_user_ids_export_sales[0].lang,
                "user_name": self.env.user.name,
                "process_time": process_log.process_datetime.strftime("%d:%m:%Y:%H:%M:%S"),
                "process_log": process_log.name
            })
            warehouse.export_sales_email_template_id.with_context(ctx).send_mail(warehouse.id)

        return True

    def export_so_pickings_to_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.ftp_server_id.state == "confirmed" and warehouse.is_auto_export_sales:
                vals = {
                    "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                    "process_datetime": fields.datetime.now(),
                    "application": "sales",
                    "operation": "export",
                    "company_id": warehouse.company_id.id
                }
                process_log = self.env["process.log"].create(vals)
                self.export_so_pickings_to_3pl(warehouse, process_log)
        return True

    def create_sr_excel_file_for_3pl(self, warehouse, process_log):
        try:
            process_log_line_obj = self.env["process.log.line"]
            if not self:
                raise UserError(_("Data not available for export pickings. Select at least 1 picking to export."))
            temp_location = tempfile.mkstemp()[1]
            workbook = xlsxwriter.Workbook(temp_location + '.xlsx')

            cell_data_format = workbook.add_format({
                'align': 'left', 'border': 1, 'size': 10})
            cell_amount_format = workbook.add_format({
                'align': 'right', 'border': 1, 'size': 10})
            try:
                worksheet = workbook.add_worksheet("product")
                row, column = 0, 0
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 25)
                worksheet.set_column('D:D', 15)
                worksheet.set_column('E:E', 15)
                worksheet.set_column('F:F', 10)
                worksheet.set_column('G:G', 20)
                worksheet.set_column('H:H', 25)
                worksheet.set_column('I:I', 25)
                worksheet.set_column('J:J', 10)
                worksheet.set_column('K:K', 10)
                worksheet.set_column('L:L', 15)
                worksheet.set_column('M:M', 15)
                worksheet.set_column('N:N', 15)
                worksheet.set_column('O:O', 15)
                worksheet.set_column('P:P', 15)
                worksheet.set_column('Q:Q', 15)
                worksheet.set_column('R:R', 15)
                worksheet.set_column('S:S', 15)
                worksheet.set_column('T:T', 15)
                worksheet.set_column('U:U', 15)
                worksheet.set_column('V:V', 15)
                worksheet.set_column('W:W', 15)

                # Report Headers
                worksheet.write(row, 0, 'Delivery Ref.', cell_data_format)
                worksheet.write(row, 1, 'Picking Ref.', cell_data_format)
                worksheet.write(row, 2, 'Source Document', cell_data_format)
                worksheet.write(row, 3, 'Tracking reference', cell_data_format)
                worksheet.write(row, 4, 'Tracking link', cell_data_format)
                worksheet.write(row, 5, 'Product Internal Reference', cell_data_format)
                worksheet.write(row, 6, 'Product Name', cell_data_format)
                worksheet.write(row, 7, 'Product Barcode', cell_data_format)
                worksheet.write(row, 8, 'Quantity', cell_data_format)
                worksheet.write(row, 9, 'Delivery Name', cell_data_format)
                worksheet.write(row, 10, 'Company Name', cell_data_format)
                worksheet.write(row, 11, 'Delivery Street', cell_data_format)
                worksheet.write(row, 12, 'Delivery Street2', cell_data_format)
                worksheet.write(row, 13, 'Delivery City', cell_data_format)
                worksheet.write(row, 14, 'Delivery Zip', cell_data_format)
                worksheet.write(row, 15, 'Delivery State', cell_data_format)
                worksheet.write(row, 16, 'Delivery Country', cell_data_format)
                worksheet.write(row, 17, 'Delivery Email', cell_data_format)
                worksheet.write(row, 18, 'Delivery Mobile', cell_data_format)
                worksheet.write(row, 19, 'Return Reason', cell_data_format)
                worksheet.write(row, 20, 'Lot/Serial Number', cell_data_format)
                worksheet.write(row, 21, 'Done Quantity', cell_data_format)
                worksheet.write(row, 22, 'Status', cell_data_format)
                row += 1
                for move in self.mapped("move_ids_without_package"):
                    if move.origin_returned_move_id:
                        try:
                            line_skipped = True
                            process_log_line_vals = {
                                "process_log_id": process_log.id,
                                "product_id": move.product_id.id,
                                "picking_id": move.picking_id.id,
                                "is_mismatch": False,
                                "message": "Line Exported Successfully For Return Picking %s , Product %s" % (move.picking_id.name, move.product_id.display_name)
                            }
                            process_log_line = process_log_line_obj.create(process_log_line_vals)
                            for rec in move:
                                if rec.picking_id.state == 'draft':
                                    status = "Draft"
                                elif rec.picking_id.state == 'waiting':
                                    status = "Waiting Another Operation"
                                elif rec.picking_id.state == 'confirmed':
                                    status = "Waiting"
                                elif rec.picking_id.state == 'assigned':
                                    status = "Ready"
                                elif rec.picking_id.state == 'done':
                                    status = "Done"
                                elif rec.picking_id.state == 'cancel':
                                    status = "Cancelled"
                                else:
                                    status = " - "

                            lot_number = ''
                            for move_line in move.move_line_ids:
                                if move.product_id and move.product_id.tracking == 'lot':
                                    lot_number = move_line.lot_id.name or ''
                                elif move.product_id and move.product_id.tracking == "serial":
                                    if move_line.lot_id.name:
                                        lot_number += move_line.lot_id.name + ","
                            lot_number = lot_number.rstrip(',')
                            text_note = ''
                            if move.picking_id.note:
                                text_note = html2plaintext(move.picking_id.note)
                            # text_note = excel_note.get_text()
                            # Product Details
                            worksheet.write(row, 0, move.origin_returned_move_id.picking_id.name, cell_data_format)
                            worksheet.write(row, 1, move.picking_id.name, cell_data_format)
                            worksheet.write(row, 2, move.picking_id.origin or '', cell_data_format)
                            worksheet.write(row, 3, move.picking_id.carrier_tracking_ref or '', cell_data_format)
                            worksheet.write(row, 4, move.picking_id.carrier_tracking_url or '', cell_data_format)
                            worksheet.write(row, 5, move.product_id.default_code, cell_data_format)
                            worksheet.write(row, 6, move.product_id.display_name, cell_data_format)
                            worksheet.write(row, 7, move.product_id.barcode, cell_amount_format)
                            worksheet.write(row, 8, move.product_uom_qty, cell_amount_format)
                            worksheet.write(row, 9, move.picking_id.partner_id.name, cell_amount_format)
                            worksheet.write(row, 10, move.picking_id.partner_id.parent_id.name or '', cell_amount_format)
                            worksheet.write(row, 11, move.picking_id.partner_id.street or '', cell_data_format)
                            worksheet.write(row, 12, move.picking_id.partner_id.street2 or '', cell_data_format)
                            worksheet.write(row, 13, move.picking_id.partner_id.city or '', cell_data_format)
                            worksheet.write(row, 14, move.picking_id.partner_id.zip or '', cell_data_format)
                            worksheet.write(row, 15, move.picking_id.partner_id.state_id.name or '', cell_data_format)
                            worksheet.write(row, 16, move.picking_id.partner_id.country_id.name or '', cell_data_format)
                            worksheet.write(row, 17, move.picking_id.partner_id.email or '', cell_data_format)
                            worksheet.write(row, 18, move.picking_id.partner_id.mobile or '', cell_data_format)
                            worksheet.write(row, 19, text_note or '', cell_data_format)
                            worksheet.write(row, 20, lot_number or '', cell_data_format)
                            worksheet.write(row, 21, move.quantity or '', cell_data_format)
                            worksheet.write(row, 22, status or '', cell_data_format)

                            row += 1
                            line_skipped = False
                            move.is_exported = True
                            if move.picking_id.move_ids_without_package.mapped("is_exported"):
                                move.picking_id.is_exported = True

                            process_log_line.write({
                                "exported_qty": move.product_uom_qty,
                                "file_qty": move.product_uom_qty
                            })

                        except Exception as e:
                            message = "Facing issue while exporting sales return pickings : %s" % e
                            process_log_line.write({
                                "message": message,
                                "is_mismatch": True,
                                "is_skip_line": line_skipped
                            })

            except Exception as e:
                process_log.note = "Facing issue in export sales return process : %s" % e
            workbook.close()

            fp = open(temp_location + '.xlsx', 'rb')
            file_name = '%sexport_%s.xlsx' % (warehouse.export_sale_return_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
            process_log.file_name = file_name
            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_sale_return_to.path, file_name)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(fp, dest_path)
                else:
                    sftp_instance.storbinary(f'STOR {file_name}', fp)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export return pickings process : %s" % e

            return True
        except Exception as e:
            process_log.note = "Facing issue in export return pickings process : %s" % e

    def create_sr_csv_file_for_3pl(self, warehouse, process_log):
        file_name = '%sexport_%s.csv' % (
        warehouse.export_sale_return_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
        process_log.file_name = file_name
        process_log_line_obj = self.env["process.log.line"]
        with open(file_name, 'w+') as csvfile:
            header_names = [
                "Delivery Ref.",
                "Picking Ref.",
                "Source Document",
                "Tracking reference",
                "Tracking link",
                "Product Internal Reference",
                "Product Name",
                "Product Barcode",
                "Quantity",
                "Delivery Name",
                "Company Name",
                "Delivery Street",
                "Delivery Street2",
                "Delivery City",
                "Delivery Zip",
                "Delivery State",
                "Delivery Country",
                "Delivery Email",
                "Delivery Mobile",
                "Note",
                "Lot/Serial Number",
                "Done Quantity",
                "Status"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=header_names)

            writer.writeheader()
            for move in self.mapped("move_ids_without_package"):
                line_skipped = True
                process_log_line_vals = {
                    "process_log_id": process_log.id,
                    "product_id": move.product_id.id,
                    "picking_id": move.picking_id.id,
                    "is_mismatch": False,
                    "message": "Line Exported Successfully For Picking %s , Product %s" % (move.picking_id.name, move.product_id.display_name)
                }
                process_log_line = process_log_line_obj.create(process_log_line_vals)
                for rec in move:
                    if rec.picking_id.state == 'draft':
                        status = "Draft"
                    elif rec.picking_id.state == 'waiting':
                        status = "Waiting Another Operation"
                    elif rec.picking_id.state == 'confirmed':
                        status = "Waiting"
                    elif rec.picking_id.state == 'assigned':
                        status = "Ready"
                    elif rec.picking_id.state == 'done':
                        status = "Done"
                    elif rec.picking_id.state == 'cancel':
                        status = "Cancelled"
                    else:
                        status = " - "

                lot_number = ''
                for move_line in move.move_line_ids:
                    if move.product_id and move.product_id.tracking == 'lot':
                        lot_number = move_line.lot_id.name or ''
                    elif move.product_id and move.product_id.tracking == "serial":
                        if move_line.lot_id.name:
                            lot_number += move_line.lot_id.name + ","
                lot_number = lot_number.rstrip(',')
                text_note = ''
                if move.picking_id.note:
                    text_note = html2plaintext(move.picking_id.note)
                # text_note = excel_note.get_text()
                try:
                    picking_data = {
                        "Delivery Ref.": move.origin_returned_move_id.picking_id.name,
                        "Picking Ref.": move.picking_id.name,
                        "Source Document": move.picking_id.origin or '',
                        "Tracking reference": move.picking_id.carrier_tracking_ref or '',
                        "Tracking link": move.picking_id.carrier_tracking_url or '',
                        "Product Internal Reference": move.product_id.default_code,
                        "Product Name": move.product_id.display_name,
                        "Product Barcode": move.product_id.barcode,
                        "Quantity": move.product_uom_qty,
                        "Delivery Name": move.picking_id.partner_id.name,
                        "Company Name": move.picking_id.partner_id.parent_id.name or '',
                        "Delivery Street": move.picking_id.partner_id.street or '',
                        "Delivery Street2": move.picking_id.partner_id.street2 or '',
                        "Delivery City": move.picking_id.partner_id.city or '',
                        "Delivery Zip": move.picking_id.partner_id.zip or '',
                        "Delivery State": move.picking_id.partner_id.state_id.name or '',
                        "Delivery Country": move.picking_id.partner_id.country_id.name or '',
                        "Delivery Email": move.picking_id.partner_id.email or '',
                        "Delivery Mobile": move.picking_id.partner_id.mobile or '',
                        "Note": text_note or '',
                        "Lot/Serial Number": lot_number or '',
                        "Done Quantity": move.quantity or '',
                        "Status": status or ''
                    }
                    writer.writerow(picking_data)
                    line_skipped = False
                    move.is_exported = True
                    if move.picking_id.move_ids_without_package.mapped("is_exported"):
                        move.picking_id.is_exported = True
                    process_log_line.write({
                        "exported_qty": move.product_uom_qty,
                        "file_qty": move.product_uom_qty
                    })
                except Exception as e:
                    message = "Facing issue while exporting sales return pickings : %s" % e
                    process_log_line.write({
                        "message": message,
                        "is_mismatch": True,
                        "is_skip_line": line_skipped
                    })

            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_sale_return_to.path, file_name)
                csvfile.seek(0)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(csvfile, dest_path)
                else:
                    with open(file_name, 'rb') as csvfile:
                        sftp_instance.storbinary(f'STOR {file_name}', csvfile)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export sales return process : %s" % e

            return True

    def export_sr_pickings_to_3pl(self, warehouse, process_log):
        stock_move_obj = self.env["stock.move"]
        pickings = self
        if not pickings:
            move_domain = [("picking_id.picking_type_code", "=", "incoming"),
                           ("origin_returned_move_id", "!=", False),
                           ("picking_id.is_exported", "=", False),
                           ('warehouse_id', '=', warehouse.id)]
            if warehouse.last_export_sale_return_datetime:
                move_domain.append(("create_date", ">", warehouse.last_export_sale_return_datetime))
            moves = stock_move_obj.search(move_domain)
            pickings = moves.mapped("picking_id")
        if warehouse.export_sales_return_file_type == "excel":
            pickings.create_sr_excel_file_for_3pl(warehouse, process_log)
        else:
            pickings.create_sr_csv_file_for_3pl(warehouse, process_log)

        warehouse.last_export_sale_return_datetime = fields.datetime.now()

        if warehouse.is_notify_users_when_export_sales_return:
            ctx = dict(self._context)
            ctx.update({
                "email_to": ",".join(warehouse.notify_user_ids_export_sales_return.mapped("partner_id").mapped("email_formatted")),
                "language": warehouse.notify_user_ids_export_sales_return[0].lang,
                "user_name": self.env.user.name,
                "process_time": process_log.process_datetime.strftime("%d:%m:%Y:%H:%M:%S"),
                "process_log": process_log.name
            })
            warehouse.export_sales_return_email_template_id.with_context(ctx).send_mail(warehouse.id)

    def export_sr_pickings_to_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.ftp_server_id.state == "confirmed" and warehouse.is_auto_export_sales_return:
                vals = {
                    "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                    "process_datetime": fields.datetime.now(),
                    "application": "sales_return",
                    "operation": "export",
                    "company_id": warehouse.company_id.id
                }
                process_log = self.env["process.log"].create(vals)
                self.export_sr_pickings_to_3pl(warehouse, process_log)
        return True

    def create_po_excel_file_for_3pl(self, warehouse, process_log):
        try:
            process_log_line_obj = self.env["process.log.line"]
            if not self:
                raise UserError(_("Data not available for export pickings. Select at least 1 picking to export."))
            temp_location = tempfile.mkstemp()[1]
            workbook = xlsxwriter.Workbook(temp_location + '.xlsx')

            cell_data_format = workbook.add_format({
                'align': 'left', 'border': 1, 'size': 10})
            cell_amount_format = workbook.add_format({
                'align': 'right', 'border': 1, 'size': 10})

            try:
                worksheet = workbook.add_worksheet("product")
                row, column = 0, 0
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('C:C', 25)
                worksheet.set_column('D:D', 15)
                worksheet.set_column('E:E', 10)
                worksheet.set_column('F:F', 25)
                worksheet.set_column('G:G', 25)
                worksheet.set_column('H:H', 25)
                worksheet.set_column('I:I', 25)
                worksheet.set_column('I:I', 25)
                worksheet.set_column('J:J', 25)
                worksheet.set_column('K:K', 25)
                worksheet.set_column('L:L', 25)
                worksheet.set_column('M:M', 25)
                worksheet.set_column('N:N', 25)
                worksheet.set_column('O:O', 25)
                worksheet.set_column('P:P', 25)

                # Report Headers
                worksheet.write(row, 0, 'Receipt Ref.', cell_data_format)
                worksheet.write(row, 1, 'Source Document', cell_data_format)
                worksheet.write(row, 2, 'Tracking reference', cell_data_format)
                worksheet.write(row, 3, 'Tracking link', cell_data_format)
                worksheet.write(row, 4, 'Internal Reference', cell_data_format)
                worksheet.write(row, 5, 'Product Name', cell_data_format)
                worksheet.write(row, 6, 'Product Barcode', cell_data_format)
                worksheet.write(row, 7, 'Quantity', cell_data_format)
                worksheet.write(row, 8, 'Vendor Name', cell_data_format)
                worksheet.write(row, 9, 'Company Name', cell_data_format)
                worksheet.write(row, 10, 'Vendor Mail', cell_data_format)
                worksheet.write(row, 11, 'Vendor Mobile', cell_data_format)
                worksheet.write(row, 12, 'Note', cell_data_format)
                worksheet.write(row, 13, 'Lot/Serial Number', cell_data_format)
                worksheet.write(row, 14, 'Done Quantity', cell_data_format)
                worksheet.write(row, 15, 'Status', cell_data_format)
                row += 1
                for move in self.mapped("move_ids_without_package"):
                    try:
                        line_skipped = True
                        process_log_line_vals = {
                            "process_log_id": process_log.id,
                            "product_id": move.product_id.id,
                            "picking_id": move.picking_id.id,
                            "is_mismatch": False,
                            "message": "Line Exported Successfully For Purchase Picking %s , Product %s" % (move.picking_id.name, move.product_id.display_name)
                        }
                        process_log_line = process_log_line_obj.create(process_log_line_vals)
                        for rec in move:
                            if rec.picking_id.state == 'draft':
                                status = "Draft"
                            elif rec.picking_id.state == 'waiting':
                                status = "Waiting Another Operation"
                            elif rec.picking_id.state == 'confirmed':
                                status = "Waiting"
                            elif rec.picking_id.state == 'assigned':
                                status = "Ready"
                            elif rec.picking_id.state == 'done':
                                status = "Done"
                            elif rec.picking_id.state == 'cancel':
                                status = "Cancelled"
                            else:
                                status = " - "

                        lot_number = ''
                        for move_line in move.move_line_ids:
                            if move.product_id and move.product_id.tracking == 'lot':
                                lot_number = move_line.lot_id.name or ''
                            elif move.product_id and move.product_id.tracking == "serial":
                                if move_line.lot_id.name:
                                    lot_number += move_line.lot_id.name + ","
                        lot_number = lot_number.rstrip(',')
                        text_note = ''
                        if move.picking_id.note:
                            text_note = html2plaintext(move.picking_id.note)
                        # text_note = excel_note.get_text()
                        # Product Details
                        worksheet.write(row, 0, move.picking_id.name, cell_data_format)
                        worksheet.write(row, 1, move.picking_id.origin or '', cell_data_format)
                        worksheet.write(row, 2, move.picking_id.carrier_tracking_ref or '', cell_data_format)
                        worksheet.write(row, 3, move.picking_id.carrier_tracking_url or '', cell_data_format)
                        worksheet.write(row, 4, move.product_id.default_code, cell_data_format)
                        worksheet.write(row, 5, move.product_id.display_name, cell_data_format)
                        worksheet.write(row, 6, move.product_id.barcode, cell_data_format)
                        worksheet.write(row, 7, move.product_uom_qty, cell_amount_format)
                        worksheet.write(row, 8, move.picking_id.partner_id.name, cell_data_format)
                        worksheet.write(row, 9, move.picking_id.partner_id.parent_id.name or '', cell_data_format)
                        worksheet.write(row, 10, move.picking_id.partner_id.email or '', cell_data_format)
                        worksheet.write(row, 11, move.picking_id.partner_id.mobile or '', cell_data_format)
                        worksheet.write(row, 12, text_note or '', cell_data_format)
                        worksheet.write(row, 13, lot_number or '', cell_data_format)
                        worksheet.write(row, 14, move.quantity or '', cell_data_format)
                        worksheet.write(row, 15, status or '', cell_data_format)

                        row += 1
                        line_skipped = False
                        move.is_exported = True
                        if move.picking_id.move_ids_without_package.mapped("is_exported"):
                            move.picking_id.is_exported = True

                        process_log_line.write({
                            "exported_qty": move.product_uom_qty,
                            "file_qty": move.product_uom_qty
                        })

                    except Exception as e:
                        message = "Facing issue while exporting po pickings : %s" % e
                        process_log_line.write({
                            "message": message,
                            "is_mismatch": True,
                            "is_skip_line": line_skipped
                        })

            except Exception as e:
                process_log.note = "Facing issue in export Purchase process : %s" % e
            workbook.close()

            fp = open(temp_location + '.xlsx', 'rb')
            file_name = '%sexport_%s.xlsx' % (warehouse.export_purchase_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
            process_log.file_name = file_name
            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_purchase_to.path, file_name)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(fp, dest_path)
                else:
                    sftp_instance.storbinary(f'STOR {file_name}', fp)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export Purchase pickings process : %s" % e
            return True
        except Exception as e:
            process_log.note = "Facing issue in export Purchase pickings process : %s" % e

    def create_po_csv_file_for_3pl(self, warehouse, process_log):
        file_name = '%sexport_%s.csv' % (warehouse.export_purchase_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
        process_log.file_name = file_name
        process_log_line_obj = self.env["process.log.line"]
        with open(file_name, 'w+') as csvfile:
            header_names = [
                "Picking Ref.",
                "Source Document",
                "Tracking reference",
                "Tracking link",
                "Internal Reference",
                "Product Name",
                "Product Barcode",
                "Quantity",
                "Vendor Name",
                "Company Name",
                "Vendor Email",
                "Vendor Mobile",
                "Note",
                "Lot/Serial Number",
                "Done Quantity",
                "Status"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=header_names)

            writer.writeheader()
            for move in self.mapped("move_ids_without_package"):
                line_skipped = True
                process_log_line_vals = {
                    "process_log_id": process_log.id,
                    "product_id": move.product_id.id,
                    "picking_id": move.picking_id.id,
                    "is_mismatch": False,
                    "message": "Line Exported Successfully For Picking %s , Product %s" % (move.picking_id.name, move.product_id.display_name)
                }
                process_log_line = process_log_line_obj.create(process_log_line_vals)
                for rec in move:
                    if rec.picking_id.state == 'draft':
                        status = "Draft"
                    elif rec.picking_id.state == 'waiting':
                        status = "Waiting Another Operation"
                    elif rec.picking_id.state == 'confirmed':
                        status = "Waiting"
                    elif rec.picking_id.state == 'assigned':
                        status = "Ready"
                    elif rec.picking_id.state == 'done':
                        status = "Done"
                    elif rec.picking_id.state == 'cancel':
                        status = "Cancelled"
                    else:
                        status = " - "

                lot_number = ''
                for move_line in move.move_line_ids:
                    if move.product_id and move.product_id.tracking == 'lot':
                        lot_number = move_line.lot_id.name or ''
                    elif move.product_id and move.product_id.tracking == "serial":
                        if move_line.lot_id.name:
                            lot_number += move_line.lot_id.name + ","
                lot_number = lot_number.rstrip(',')
                text_note = ''
                if move.picking_id.note:
                    text_note = html2plaintext(move.picking_id.note)
                # text_note = excel_note.get_text()
                try:
                    picking_data = {
                        "Picking Ref.": move.picking_id.name,
                        "Source Document": move.picking_id.origin or '',
                        "Tracking reference": move.picking_id.carrier_tracking_ref or '',
                        "Tracking link": move.picking_id.carrier_tracking_url or '',
                        "Internal Reference": move.product_id.default_code,
                        "Product Name": move.product_id.display_name,
                        "Product Barcode": move.product_id.barcode,
                        "Quantity": move.product_uom_qty,
                        "Vendor Name": move.picking_id.partner_id.name,
                        "Company Name": move.picking_id.partner_id.parent_id.name or '',
                        "Vendor Email": move.picking_id.partner_id.email or '',
                        "Vendor Mobile": move.picking_id.partner_id.mobile or '',
                        "Note": text_note or '',
                        "Lot/Serial Number": lot_number or '',
                        "Done Quantity": move.quantity or '',
                        "Status": status or '',
                    }
                    writer.writerow(picking_data)
                    line_skipped = False
                    move.is_exported = True
                    if move.picking_id.move_ids_without_package.mapped("is_exported"):
                        move.picking_id.is_exported = True

                    process_log_line.write({
                        "exported_qty": move.product_uom_qty,
                        "file_qty": move.product_uom_qty
                    })
                except Exception as e:
                    message = "Facing issue while exporting purchase pickings : %s" % e
                    process_log_line.write({
                        "message": message,
                        "is_mismatch": True,
                        "is_skip_line": line_skipped
                    })

            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_purchase_to.path, file_name)
                csvfile.seek(0)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(csvfile, dest_path)
                else:
                    with open(file_name, 'rb') as csvfile:
                        sftp_instance.storbinary(f'STOR {file_name}', csvfile)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export purchase process : %s" % e

            return True

    def export_po_pickings_to_3pl(self, warehouse, process_log):
        stock_move_obj = self.env["stock.move"]
        pickings = self
        if not pickings:
            move_domain = [("picking_id.picking_type_code", "=", "incoming"),
                           ("origin_returned_move_id", "=", False),
                           ("picking_id.is_exported", "=", False),
                           ('warehouse_id', '=', warehouse.id)]
            if warehouse.last_export_purchase_datetime:
                move_domain.append(("create_date", ">", warehouse.last_export_purchase_datetime))
            moves = stock_move_obj.search(move_domain)
            pickings = moves.mapped("picking_id")
        if warehouse.export_purchase_file_type == "excel":
            pickings.create_po_excel_file_for_3pl(warehouse, process_log)
        else:
            pickings.create_po_csv_file_for_3pl(warehouse, process_log)

        warehouse.last_export_purchase_datetime = fields.datetime.now()

        if warehouse.is_notify_users_when_export_purchase:
            ctx = dict(self._context)
            ctx.update({
                "email_to": ",".join(warehouse.notify_user_ids_export_purchase.mapped("partner_id").mapped("email_formatted")),
                "language": warehouse.notify_user_ids_export_purchase[0].lang,
                "user_name": self.env.user.name,
                "process_time": process_log.process_datetime.strftime("%d:%m:%Y:%H:%M:%S"),
                "process_log": process_log.name
            })
            warehouse.export_purchase_email_template_id.with_context(ctx).send_mail(warehouse.id)

    def export_po_pickings_to_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.ftp_server_id.state == "confirmed" and warehouse.is_auto_export_purchase:
                vals = {
                    "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                    "process_datetime": fields.datetime.now(),
                    "application": "purchase",
                    "operation": "export",
                    "company_id": warehouse.company_id.id
                }
                process_log = self.env["process.log"].create(vals)
                self.export_po_pickings_to_3pl(warehouse, process_log)
        return

    def get_list_serial_evaluate(self, serial_num_list=[]):
        serial_num_updated_list = []
        for serial in serial_num_list:
            try:
                if float(serial).is_integer():
                    serial_num_updated_list.append(int(float(serial)))
                else:
                    serial_num_updated_list.append(serial)
            except:
                serial_num_updated_list.append(serial)
        return serial_num_updated_list

    def import_so_response_excel_process(self, local_path, process_log, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]
        file_data = {}
        if warehouse.ftp_server_id.connection_type == 'sftp':
            workbook = xlrd.open_workbook('%s' % local_path)
        else:
            workbook = xlrd.open_workbook('%s' % local_path)
        sheet = workbook.sheet_by_index(0)
        import_so_file = False
        for row_count in range(sheet.nrows):
            try:
                row_list = sheet.row_values(row_count, 0, sheet.ncols)
                if not import_so_file:
                    if row_list[0] != "Picking Ref." or row_list[4] != "Product Internal Reference" or row_list[5] != "Product Name":
                        return {}
                import_so_file = True
                product_ref = row_list[4]
                product_barcode = row_list[6]
                if row_list[0].lower() == "picking ref.":
                    continue
                line_skipped = True
                process_log_line = process_log_line_obj.create({
                    "process_log_id": process_log.id,
                    "is_mismatch": False,
                })

                product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                if not product:
                    product = product_obj.search([("barcode", "=", product_barcode)], limit=1)
                if not product:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Product Not Found For Line : %s" % row_list
                    })
                    continue
                process_log_line.product_id = product.id
                picking = self.search([("name", "=", row_list[0]), ("state", "not in", ["done", "cancel"])])
                if row_list[2]:
                    picking.write({'carrier_tracking_ref': row_list[2]})
                process_log_line.picking_id = picking.id
                if len(row_list) != 22 or row_list[21] not in ['Done', 'Delivered']:
                    picking = False
                if not picking:
                    picking = self.search([("name", "=", row_list[0]), ("state", "in", ["done", "cancel"])])
                    if picking:
                        picking_state = "Done"
                        if picking.state == "cancel":
                            picking_state = "Cancel"
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "picking %s is in %s state." % (row_list[0], picking_state)
                        })
                        continue
                if not picking:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Picking Not Found For Line : %s" % row_list
                    })
                    continue

                tmp_data = file_data.get(picking, {})
                lot_id = False
                serial_num = []
                if product.tracking == 'lot' and row_list[19]:
                    lot_no = row_list[19]
                    if lot_no and lot_no.is_integer():
                        lot_no = int(lot_no)
                    lot_id = self.env['stock.lot'].search([
                        ('name', '=', str(lot_no)),
                        ('product_id', '=', product.id),
                        ('company_id', '=', warehouse.company_id.id)], limit=1).id
                    if not lot_id:
                        vals = {
                            "name": str(lot_no),
                            "product_id": product.id,
                            "product_qty": int(row_list[20]),
                            "company_id": warehouse.company_id.id
                        }
                        lot_id = self.env['stock.lot'].create(vals).id
                if product.tracking == 'serial' and row_list[19]:
                    row_list_lot = str(row_list[19]).split(',')
                    if int(row_list[20]) != len(row_list_lot):
                        raise ValidationError(('Please add serial number as defined quantity'))
                    else:
                        row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                        for lot_no in row_list_lot_updated:
                            serial_no = self.env['stock.lot'].search([
                                ('name', '=', lot_no),
                                ('product_id', '=', product.id),
                                ('company_id', '=', warehouse.company_id.id)], limit=1)

                            if not serial_no:
                                vals = {
                                    "name": lot_no,
                                    "product_id": product.id,
                                    "product_qty": 1,
                                    "company_id": warehouse.company_id.id,
                                }
                                serial_no = self.env['stock.lot'].create(vals)
                                # self.env['stock.quant'].create({
                                #     'product_id': product.id,
                                #     'location_id': warehouse.lot_stock_id.id,
                                #     'reserved_quantity': 0,
                                #     'available_quantity': 1,
                                #     'serial_no': lot_no.id})
                            serial_num.append(serial_no.id)
                            
                tmp_data.update({
                    product: {
                        "lot_id": lot_id if lot_id else serial_num,
                        "quantity": row_list[20],
                        "status": row_list[21]
                    }
                })

                file_data.update({picking: tmp_data})
                line_skipped = False
            except Exception as e:
                if product.tracking == 'serial' and row_list[19]:
                    row_list_lot = str(row_list[19]).split(',')
                    if int(row_list[20]) != len(row_list_lot):
                        process_log_line.write({
                            "is_skip_line": line_skipped,
                            "is_mismatch": True,
                            "message": "Please add serial number as defined quantity for line: %s" % row_list[5]
                        })
                    else:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Error While Processing Line : %s Error : %s" % (row_list, e)
                        })
                else:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Error While Processing Line : %s Error : %s" % (row_list, e)
                    })
                continue
        return file_data

    def import_so_response_csv_process(self, local_path, process_log, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]
        file_data = {}

        try:
            local_path_open = '$%s' % local_path
            check_file = open(local_path_open, mode='r')
        except Exception as e:
            local_path_open = '%s' % local_path

        with open(local_path_open, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            import_so_file = False
            for row in csv_reader:
                try:
                    line_skipped = True
                    keys_list = list(row.keys())
                    if not import_so_file:
                        if keys_list[0] != "Picking Ref." or keys_list[4] != "Product Internal Reference" or keys_list[5] != "Product Name":
                            return {}
                    import_so_file = True
                    process_log_line = process_log_line_obj.create({
                        "process_log_id": process_log.id,
                        "is_mismatch": False,
                    })

                    product_ref = row.get("Product Internal Reference", False)
                    product_barcode = row.get("Product Barcode", False)

                    product = product_ref and product_obj.search([("default_code", "=", product_ref)], limit=1)
                    if not product:
                        product = product_barcode and product_obj.search([("barcode", "=", product_barcode)], limit=1)
                    if not product:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Product Not Found For Line : %s" % row
                        })
                        continue
                    process_log_line.product_id = product.id

                    if not row.get("Picking Ref.", False):
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Picking Ref Not Found In Line : %s" % row
                        })
                        continue

                    picking = self.search(
                        [("name", "=", row.get("Picking Ref.")), ("state", "not in", ["done", "cancel"])])

                    if 'Status' not in row or row.get('Status') not in ['Done', 'Delivered']:
                        picking = False

                    if not picking:
                        picking = self.search([("name", "=", row.get("Picking Ref.")), ("state", "in", ["done", "cancel"])])
                        if picking:
                            picking_state = "Done"
                            if picking.state == "cancel":
                                picking_state = "Cancel"
                            process_log_line.write({
                                "is_mismatch": True,
                                "is_skip_line": line_skipped,
                                "message": "picking %s is in %s state." % (row.get("Picking Ref."), picking_state)
                            })

                    if not picking:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Picking Not Found For Line : %s" % row
                        })
                        continue
                    process_log_line.picking_id = picking.id

                    tmp_data = file_data.get(picking, {})
                    lot_id = False
                    serial_num = []
                    if product.tracking == 'lot' and row.get("Lot/Serial Number"):
                        lot_id = self.env['stock.lot'].search([
                            ('name', '=', row.get("Lot/Serial Number")),
                            ('product_id', '=', product.id),
                            ('company_id', '=', warehouse.company_id.id)], limit=1).id
                        if not lot_id:
                            vals = {
                                "name": row.get("Lot/Serial Number"),
                                "product_id": product.id,
                                "product_qty": eval(row.get("Done Quantity")),
                                "company_id": warehouse.company_id.id
                            }
                            lot_id = self.env['stock.lot'].create(vals).id

                    if product.tracking == 'serial' and row.get("Lot/Serial Number"):
                        row_list_lot = row.get("Lot/Serial Number").split(',')
                        if eval(row.get("Done Quantity")) != len(row_list_lot):
                            raise ValidationError(_('Please add serial number as defined quantity'))
                        else:
                            row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                            for lot in row_list_lot_updated:
                                lot_no = self.env['stock.lot'].search([
                                    ('name', '=', lot),
                                    ('product_id', '=', product.id),
                                    ('company_id', '=', warehouse.company_id.id)], limit=1)

                                if not lot_no:
                                    vals = {
                                        "name": lot,
                                        "product_id": product.id,
                                        "product_qty": 1,
                                        "company_id": warehouse.company_id.id,
                                    }
                                    lot_no = self.env['stock.lot'].create(vals)
                                    self.env['stock.quant'].create({
                                        'product_id': product.id,
                                        'location_id': warehouse.lot_stock_id.id,
                                        'reserved_quantity': 0,
                                        'available_quantity': 1,
                                        'lot_id': lot_no.id})
                                serial_num.append(lot_no.id)
                    tmp_data.update({
                        product: {
                            "lot_id": lot_id if lot_id else serial_num,
                            "quantity": row.get("Done Quantity", 0.0),
                            "status": row.get("Status", "-")
                        }
                    })
                    file_data.update({picking: tmp_data})
                    line_skipped = False
                except Exception as e:
                    if row.get("Status") == 'Done':
                        process_log_line.write({
                            "is_skip_line": line_skipped,
                            "is_mismatch": True,
                            "message": "Status not done %s" % row
                            })
                    if product.tracking == 'serial' and row.get("Lot/Serial Number"):
                        row_list_lot = row.get("Lot/Serial Number").split(',')
                        row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                        if eval(row.get("Done Quantity")) != len(row_list_lot):
                            process_log_line.write({
                                "is_skip_line": line_skipped,
                                "is_mismatch": True,
                                "message": "Please add serial number as defined quantity for line: %s" % row
                            })
                    else:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Error While Processing Line : %s" % row
                        })
                    continue
        return file_data

    def import_so_response_from_3pl(self, warehouse):
        process_mismatch = False
        sftp_instance = warehouse.ftp_server_id.connect_to_ftp_server()

        flag = False
        if (not warehouse.import_sales_res_from.path) or (
                warehouse.ftp_server_id.connection_type == 'sftp' and not sftp_instance.isdir(
                warehouse.import_sales_res_from.path)):
            flag = True
        if warehouse.ftp_server_id.connection_type == 'ftp':
            flag = warehouse.ftp_server_id.check_ftp_directory(sftp_instance, warehouse.import_sales_res_from.path)
        if flag:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "sales",
                "operation": "import",
                "company_id": self.env.user.company_id.id,
                "note": "Location not found on FTP Server : %s" % warehouse.import_sales_res_from.path
            }
            self.env["process.log"].create(vals)
            return True

        if warehouse.ftp_server_id.connection_type == 'sftp':
            file_list = sftp_instance.listdir(warehouse.import_sales_res_from.path)
        else:
            file_list = [name for name, facts in sftp_instance.mlsd(warehouse.import_sales_res_from.path)]
        log_files = []
        file_extension = ".xlsx"
        if warehouse.import_sales_res_file_type == "csv":
            file_extension = ".csv"

        import_files = [] # All Import file are stored here
        exported_files = [] # All Export files are stored here 
        identity_import_files = []

        for file_name in file_list:
            import_prefix = warehouse.import_sales_res_prefix
            if file_name.startswith(import_prefix):
                import_files.append(file_name)
            else:
                exported_files.append(file_name)

        for exported_file in exported_files:
            leangth = len(warehouse.export_sales_prefix)
            sliced_file = exported_file[leangth:]
            export_file = ''.join((warehouse.import_sales_res_prefix, sliced_file)) 
            export_file = export_file.rstrip(file_extension)
            identity_import_files.append(export_file)

        if len(exported_files) > 0:
            for check_file in identity_import_files:
                duplicate_file_lst = []
                for imp_files in import_files:
                    if imp_files.startswith(check_file):
                        duplicate_file_lst.append(imp_files)
                if len(duplicate_file_lst) > 1:
                    raise ValidationError(("You have duplicate '%s%s' Import Files in your directory.\nPlease remove unnecessary file to continue this process.") % (check_file , file_extension))

        stock_files_to_process = []
        for file_name in file_list:
            if file_name.startswith(warehouse.import_sales_res_prefix):
                if (warehouse.import_sales_res_file_type == 'excel' and warehouse.export_sales_file_type == 'excel') or (warehouse.import_sales_res_file_type == 'excel' and warehouse.export_sales_file_type == 'csv'):
                    if re.findall("^%s" % warehouse.import_sales_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                        if file_name.startswith(warehouse.import_sales_res_prefix) and file_name.endswith('.xlsx'):
                            stock_files_to_process.append(file_name)
                    else:
                        vals = {
                            "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                            "process_datetime": fields.datetime.now(),
                            "application": "sales",
                            "operation": "import",
                            "file_name": "Import EXCEL File Not Found!!!!!",
                            "company_id": self.env.user.company_id.id,
                            "note": "Import EXCEL File Not Found!!!!!"
                        }
                        self.env["process.log"].create(vals)
                elif (warehouse.import_sales_res_file_type == 'csv' and warehouse.export_sales_file_type == 'csv') or (warehouse.import_sales_res_file_type == 'csv' and warehouse.export_sales_file_type == 'excel'):
                    if re.findall("^%s" % warehouse.import_sales_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                        if file_name.startswith(warehouse.import_sales_res_prefix) and file_name.endswith('.csv'):
                            stock_files_to_process.append(file_name)
                    else:
                        vals = {
                            "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                            "process_datetime": fields.datetime.now(),
                            "application": "sales",
                            "file_name": "Import CSV File Not Found!!!!!",
                            "operation": "import",
                            "company_id": self.env.user.company_id.id,
                            "note": "Import CSV File Not Found!!!!!"
                        }
                        self.env["process.log"].create(vals)
                
        for file in stock_files_to_process:
            file_server_path = "%s/%s" % (warehouse.import_sales_res_from.path, file)

            if not warehouse.import_ftp_files_to:
                raise UserError("Import directory path not configured in warehouse.")

            dir_path = warehouse.import_ftp_files_to

            try:
                os.stat(dir_path)
            except:
                check_path = ""
                for dir_name in dir_path.split('/'):
                    if dir_name == "":
                        continue
                    check_path = "%s/%s" % (check_path, dir_name)
                    directory_exist = True
                    try:
                        os.stat(check_path)
                    except:
                        directory_exist = False
                    if not directory_exist and dir_name:
                        os.system("mkdir %s" % check_path)
                        os.system("chmod 777 -R %s" % check_path)

                try:
                    os.stat(check_path)
                except:
                    raise UserError("Directory not available to import file.")

            local_path = "%s/%s" % (dir_path, file)
            os.system("chmod 777 -R %s" % dir_path)

            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "sales",
                "operation": "import",
                "file_name": file,
                "company_id": self.env.user.company_id.id
            }

            process_log = self.env["process.log"].create(vals)
            log_files.append(process_log.name)
            if warehouse.ftp_server_id.connection_type == 'sftp':
                try:
                    sftp_instance.get(file_server_path, '$%s' % local_path)
                except Exception as e:
                    sftp_instance.get(file_server_path, '%s' % local_path)
            else:
                try:
                    sftp_instance.cwd(warehouse.import_sales_res_from.path)
                    sftp_instance.retrbinary("RETR " + file, open("%s/%s" % (dir_path, file), 'wb').write)
                except Exception as e:
                    process_mismatch = True
                    process_log.note = "Something went wrong while processing import sales : %s" % e

            try:
                local_path = "%s/%s" % (dir_path, file)
                if warehouse.import_sales_res_file_type == "excel":
                    file_data = self.import_so_response_excel_process(local_path, process_log, warehouse)
                else:
                    file_data = self.import_so_response_csv_process(local_path, process_log, warehouse)

                self.process_3pl_so_pickings(file_data, process_log)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    os.remove(local_path)
                else:
                    os.remove('%s' % local_path)
                file_path = "%s/%s" % (warehouse.import_sales_res_from.path, file)
                if warehouse.move_processed_sale_file_to and warehouse.move_processed_sale_file_to.path:
                    archive_path = "%s/%s" % (warehouse.move_processed_sale_file_to.path, file)
                    sftp_instance.rename(file_path, archive_path)
            except Exception as e:
                process_mismatch = True
                process_log.note = "Something went wrong while processing import sales : %s" % e

            mismatches = process_log.process_log_line_ids.filtered(lambda m: m.is_mismatch)
            if not mismatches and not process_mismatch:
                process_log.note = "Import Sales Processed Successfully!!!"

        if warehouse.is_notify_users_when_import_sales:
            ctx = dict(self._context)
            ctx.update({
                "email_to": ",".join(warehouse.notify_user_ids_import_sales.mapped("partner_id").mapped("email_formatted")),
                "language": warehouse.notify_user_ids_import_sales[0].lang,
                "user_name": self.env.user.name,
                "process_time": fields.Datetime.now().strftime("%d:%m:%Y:%H:%M:%S"),
                "process_log": log_files and log_files[0] or "-"
            })
            warehouse.import_sales_email_template_id.with_context(ctx).send_mail(warehouse.id)

        return True

    def process_3pl_so_pickings(self, file_data, process_log):
        process_log_line_obj = self.env["process.log.line"]
        product = False
        for picking, product_data in file_data.items():
            line_skipped = True
            process_log_line = False
            try:
                if picking.state == 'draft':
                    picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                move.move_line_ids.exists().unlink()
                for product, data in product_data.items():
                    process_log_line_domain = [
                        ("process_log_id", "=", process_log.id),
                        ("picking_id", "=", picking.id),
                        ("product_id", "=", product.id)
                    ]
                    process_log_line = process_log_line_obj.search(process_log_line_domain, order="id desc", limit=1)
                    move = picking.move_ids_without_package.filtered(lambda line: line.product_id == product)
                    if move:
                        if move.product_id and move.product_id.tracking == 'none':
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            move.quantity = data.get('quantity')
                        elif move.product_id and move.product_id.tracking == "serial":
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            if data.get('lot_id'):
                                lot_num = self.env['stock.lot'].browse(data.get('lot_id'))
                                for serial in lot_num:
                                    self.env['stock.move.line'].create({
                                        'lot_id': serial.id,
                                        'quantity': 1,
                                        'picking_id': picking.id,
                                        'product_id': move.product_id.id,
                                        'move_id': move.id,})
                        elif move.product_id and move.product_id.tracking == "lot":
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            if data.get('lot_id'):
                                self.env['stock.move.line'].create({
                                        'lot_id': data.get('lot_id'),
                                        'quantity': data.get('quantity'),
                                        'product_id': move.product_id.id,
                                        'picking_id': picking.id,
                                        'move_id': move.id,})

                        picking.tpl_status = data.get("status", "-")

                if picking.tpl_status in ['Done', 'Delivered']:
                    picking_so = picking.with_context(skip_immediate=True, skip_sms=True).button_validate()
                    if isinstance(picking_so, dict) and picking_so.get('res_model') == 'stock.backorder.confirmation':
                        wizard_id = self.env['stock.backorder.confirmation'].with_context(picking_so.get('context')).create({})
                        wizard_id.with_context(picking_so.get('context')).process()
                    line_skipped = False
                    self._cr.commit()

            except Exception as e:
                if not process_log_line:
                    process_log_line_domain = [
                        ("process_log_id", "=", process_log.id),
                        ("picking_id", "=", picking.id),
                    ]
                    if product:
                        process_log_line_domain.append(("product_id", "=", product.id))
                    process_log_line = process_log_line_obj.search(process_log_line_domain, order="id desc", limit=1)
                process_log_line.write({
                    "is_mismatch": True,
                    "is_skip_line": line_skipped,
                    "message": e
                })
                continue
        return True

    def import_so_response_from_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.is_auto_import_sales_res:
                self.import_so_response_from_3pl(warehouse)
        return True

    def import_sr_response_excel_process(self, local_path, process_log, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]
        file_data = {}
        if warehouse.ftp_server_id.connection_type == 'sftp':
            workbook = xlrd.open_workbook('%s' % local_path)
        else:
            workbook = xlrd.open_workbook('%s' % local_path)
        sheet = workbook.sheet_by_index(0)
        import_sr_file = False
        for row_count in range(sheet.nrows):
            try:
                row_list = sheet.row_values(row_count, 0, sheet.ncols)
                if not import_sr_file:
                    if row_list[0] != "Delivery Ref." or row_list[1] != "Picking Ref." or row_list[5] != "Product Internal Reference":                    
                        return {}
                import_sr_file = True
                product_ref = row_list[5]
                product_barcode = row_list[7]
                if row_list[0].lower() == "delivery ref.":
                    continue
                line_skipped = True
                process_log_line = process_log_line_obj.create({
                    "process_log_id": process_log.id,
                    "is_mismatch": False,
                })
                product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                if not product:
                    product = product_obj.search([("barcode", "=", product_barcode)], limit=1)
                if not product:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Product Not Found For Line : %s" % row_list
                    })
                    continue
                process_log_line.product_id = product
                picking = self.search([("name", "=", row_list[1]), ("state", "not in", ["done", "cancel"])])
                if row_list[3]:
                    picking.write({'carrier_tracking_ref': row_list[3]})
                if len(row_list) != 23 or row_list[22] not in ['Done', 'Received']:
                    picking = False

                if not picking:
                    picking = self.search([("name", "=", row_list[1]), ("state", "in", ["done", "cancel"])])
                    if picking:
                        picking_state = "Done"
                        if picking.state == "cancel":
                            picking_state = "Cancel"
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "picking %s is in %s state." % (row_list[1], picking_state)
                        })
                else:
                    picking_state = "Done"
                    if picking.state == "cancel":
                        picking_state = "Cancel"
                    process_log_line.write({
                        "message": "picking %s is in %s state." % (row_list[1], picking_state)
                    })

                if not picking:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Picking Not Found For Line : %s" % row_list
                    })
                    continue

                tmp_data = file_data.get(picking, {})
                lot_id = False
                serial_num = []
                if product.tracking == 'lot' and row_list[20]:
                    lot_no = row_list[20]
                    if lot_no.is_integer():
                        lot_no = int(lot_no)
                    lot_id = self.env['stock.lot'].search([
                        ('name', '=', str(lot_no)),
                        ('product_id', '=', product.id),
                        ('company_id', '=', warehouse.company_id.id)], limit=1).id
                    if not lot_id:
                        vals = {
                            "name": str(lot_no),
                            "product_id": product.id,
                            "product_qty": int(row_list[21]),
                            "company_id": warehouse.company_id.id
                        }
                        lot_id = self.env['stock.lot'].create(vals).id

                if product.tracking == 'serial' and row_list[20]:
                    row_list_lot = str(row_list[20]).split(',')
                    if int(row_list[21]) != len(row_list_lot):
                        raise ValidationError(('Please add serial number as defined quantity'))
                    else:
                        row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                        for lot in row_list_lot_updated:
                            lot_no = self.env['stock.lot'].search([
                                ('name', '=', lot),
                                ('product_id', '=', product.id),
                                ('company_id', '=', warehouse.company_id.id)], limit=1)

                            if not lot_no:
                                vals = {
                                    "name": lot,
                                    "product_id": product.id,
                                    "product_qty": 1,
                                    "company_id": warehouse.company_id.id,
                                }
                                lot_no = self.env['stock.lot'].create(vals)
                                self.env['stock.quant'].create({
                                    'product_id': product.id,
                                    'location_id': warehouse.lot_stock_id.id,
                                    'reserved_quantity': 0,
                                    'available_quantity': 1,
                                    'lot_id': lot_no.id})
                            serial_num.append(lot_no.id)
                            
                tmp_data.update({
                    product: {
                        "lot_id": lot_id if lot_id else serial_num,
                        "quantity": row_list[21],
                        "status": row_list[22]
                    }
                })
                file_data.update({picking: tmp_data})
                line_skipped = False

            except Exception as e:
                if product.tracking == 'serial' and row_list[20]:
                    row_list_lot = str(row_list[20]).split(',')
                    if int(row_list[21]) != len(row_list_lot):
                        process_log_line.write({
                            "is_skip_line": line_skipped,
                            "is_mismatch": True,
                            "message": "Please add serial number as defined quantity for line: %s" % row_list[20]
                        })
                    else:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Error While Processing Line : %s" % row_list
                        })
                else:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Error While Processing Line : %s" % row_list
                    })
                continue
        return file_data

    def import_sr_response_csv_process(self, local_path, process_log, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]
        file_data = {}

        try:
            local_path_open = '$%s' % local_path
            check_file = open(local_path_open, mode='r')
        except Exception as e:
            local_path_open = '%s' % local_path
        with open(local_path_open, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            import_sr_file = False
            for row in csv_reader:
                try:
                    line_skipped = True

                    keys_list = list(row.keys())
                    if not import_sr_file:
                        if keys_list[0] != "Delivery Ref." or keys_list[1] != "Picking Ref." or keys_list[5] != "Product Internal Reference":
                            return {}
                    import_sr_file = True

                    process_log_line = process_log_line_obj.create({
                        "process_log_id": process_log.id,
                        "is_mismatch": False
                    })

                    product_ref = row.get("Product Internal Reference", False)
                    product_barcode = row.get("Product Barcode", False)

                    product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                    if not product:
                        product = product_obj.search([("barcode", "=", product_barcode)], limit=1)
                    if not product:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Product Not Found For Line : %s" % row
                        })
                        continue

                    if not row.get("Picking Ref.", False):
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Picking Ref Not Found In Line : %s" % row
                        })
                        continue

                    picking = self.search(
                        [("name", "=", row.get("Picking Ref.")), ("state", "not in", ["done", "cancel"])])

                    if 'Status' not in row or row.get('Status') not in ['Done', 'Received']:
                        picking = False

                    if not picking:
                        picking = self.search([("name", "=", row.get("Picking Ref.")), ("state", "in", ["done", "cancel"])])
                        if picking:
                            picking_state = "Done"
                            if picking.state == "cancel":
                                picking_state = "Cancel"
                            process_log_line.write({
                                "is_mismatch": True,
                                "is_skip_line": line_skipped,
                                "message": "picking %s is in %s state." % (row.get("Picking Ref."), picking_state)
                            })

                    if not picking:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Picking Not Found For Line : %s" % row
                        })
                        continue

                    tmp_data = file_data.get(picking, {})

                    lot_id = False
                    serial_num = []
                    if product.tracking == 'lot' and row.get("Lot/Serial Number"):
                        lot_id = self.env['stock.lot'].search([
                            ('name', '=', row.get("Lot/Serial Number")),
                            ('product_id', '=', product.id),
                            ('company_id', '=', warehouse.company_id.id)], limit=1).id
                        if not lot_id:
                            vals = {
                                "name": row.get("Lot/Serial Number"),
                                "product_id": product.id,
                                "product_qty": eval(row.get("Done Quantity")),
                                "company_id": warehouse.company_id.id
                            }
                            lot_id = self.env['stock.lot'].create(vals).id

                    if product.tracking == 'serial' and row.get("Lot/Serial Number"):
                        row_list_lot = row.get("Lot/Serial Number").split(',')
                        if eval(row.get("Done Quantity")) != len(row_list_lot):
                            raise ValidationError(('Please add serial number as defined quantity'))
                        else:
                            row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                            for lot in row_list_lot_updated:
                                lot_no = self.env['stock.lot'].search([
                                    ('name', '=', lot),
                                    ('product_id', '=', product.id),
                                    ('company_id', '=', warehouse.company_id.id)], limit=1)

                                if not lot_no:
                                    vals = {
                                        "name": lot,
                                        "product_id": product.id,
                                        "product_qty": 1,
                                        "company_id": warehouse.company_id.id,
                                    }
                                    lot_no = self.env['stock.lot'].create(vals)
                                    self.env['stock.quant'].create({
                                        'product_id': product.id,
                                        'location_id': warehouse.lot_stock_id.id,
                                        'reserved_quantity': 0,
                                        'available_quantity': 1,
                                        'lot_id': lot_no.id})
                                serial_num.append(lot_no.id)
                                
                    tmp_data.update({
                        product: {
                            "lot_id": lot_id if lot_id else serial_num,
                            "quantity": row.get("Done Quantity", 0.0),
                            "status": row.get("Status", "-")
                        }
                    })

                    file_data.update({picking: tmp_data})
                    line_skipped = False

                except Exception as e:
                    if product.tracking == 'serial' and row.get("Lot/Serial Number"):
                        row_list_lot = row.get("Lot/Serial Number").split(',')
                        if eval(row.get("Done Quantity")) != len(row_list_lot):
                            process_log_line.write({
                                "is_skip_line": line_skipped,
                                "is_mismatch": True,
                                "message": "Please add serial number as defined quantity for line: %s" % row
                            })
                    else:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Error While Processing Line : %s" % row
                        })
                    continue
        return file_data

    def import_sr_response_from_3pl(self, warehouse):
        process_mismatch = False
        sftp_instance = warehouse.ftp_server_id.connect_to_ftp_server()
        flag = False
        if (not warehouse.import_sale_return_res_from.path) or (
                warehouse.ftp_server_id.connection_type == 'sftp' and not sftp_instance.isdir(
                warehouse.import_sale_return_res_from.path)):
            flag = True
        if warehouse.ftp_server_id.connection_type == 'ftp':
            flag = warehouse.ftp_server_id.check_ftp_directory(sftp_instance, warehouse.import_sale_return_res_from.path)
        if flag:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "sales_return",
                "operation": "import",
                "company_id": self.env.user.company_id.id,
                "note": "Location not found on FTP Server : %s" % warehouse.import_sale_return_res_from.path
            }

            self.env["process.log"].create(vals)
            return True

        if warehouse.ftp_server_id.connection_type == 'sftp':
            file_list = sftp_instance.listdir(warehouse.import_sale_return_res_from.path)
        else:
            file_list = [name for name, facts in sftp_instance.mlsd(warehouse.import_sale_return_res_from.path)]

        if len(file_list) == 0:
            raise UserError("There are no files in the directory")
        file_extension = ".xlsx"
        if warehouse.import_sales_return_res_file_type == "csv":
            file_extension = ".csv"

        import_files = [] # All Import file are stored here
        exported_files = [] # All Export files are stored here 
        identity_import_files = []

        for file_name in file_list:
            import_prefix = warehouse.import_sale_return_res_prefix
            if file_name.startswith(import_prefix):
                import_files.append(file_name)
            else:
                exported_files.append(file_name)

        for exported_file in exported_files:
            leangth = len(warehouse.export_sale_return_prefix)
            sliced_file = exported_file[leangth:]
            export_file = ''.join((warehouse.import_sale_return_res_prefix, sliced_file)) 
            export_file = export_file.rstrip(file_extension)
            identity_import_files.append(export_file)

        if len(exported_files) > 0:
            for check_file in identity_import_files:
                duplicate_file_lst = []
                for imp_files in import_files:
                    if imp_files.startswith(check_file):
                        duplicate_file_lst.append(imp_files)
                if len(duplicate_file_lst) > 1:
                    raise ValidationError(("You have duplicate '%s%s' Import Files in your directory.\n Please remove unnecessary file to continue this process.") % (check_file , file_extension))

        stock_files_to_process = []
        log_files = []
        for file_name in file_list:
            if file_name.startswith(warehouse.import_sale_return_res_prefix):
                if (warehouse.import_sales_return_res_file_type == 'excel' and warehouse.export_sales_return_file_type == 'excel') or (warehouse.import_sales_return_res_file_type == 'excel' and warehouse.export_sales_return_file_type == 'csv'):
                    if re.findall("^%s" % warehouse.import_sale_return_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                        if file_name.startswith(warehouse.import_sale_return_res_prefix) and file_name.endswith('.xlsx'):
                            stock_files_to_process.append(file_name)
                    else:
                        vals = {
                            "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                            "process_datetime": fields.datetime.now(),
                            "application": "sales_return",
                            "file_name": "Import EXCEL File Not Found!!!!!",
                            "operation": "import",
                            "company_id": self.env.user.company_id.id,
                            "note": "Import EXCEL File Not Found!!!!!"
                        }
                        self.env["process.log"].create(vals)
                elif (warehouse.import_sales_return_res_file_type == 'csv' and warehouse.export_sales_return_file_type == 'csv') or (warehouse.import_sales_return_res_file_type == 'csv' and warehouse.export_sales_return_file_type == 'excel'):
                    if re.findall("^%s" % warehouse.import_sale_return_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                        if file_name.startswith(warehouse.import_sale_return_res_prefix) and file_name.endswith('.csv'):
                            stock_files_to_process.append(file_name)
                    else:
                        vals = {
                            "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                            "process_datetime": fields.datetime.now(),
                            "application": "sales_return",
                            "file_name": "Import CSV File Not Found!!!!!",
                            "operation": "import",
                            "company_id": self.env.user.company_id.id,
                            "note": "Import CSV File Not Found!!!!!"
                        }
                        self.env["process.log"].create(vals)
        for file in stock_files_to_process:

            file_server_path = "%s/%s" % (warehouse.import_sale_return_res_from.path, file)
            if not warehouse.import_ftp_files_to:
                raise UserError("Import directory path not configured in warehouse.")

            dir_path = warehouse.import_ftp_files_to

            try:
                os.stat(dir_path)
            except:
                check_path = ""
                for dir_name in dir_path.split('/'):
                    if dir_name == "":
                        continue
                    check_path = "%s/%s" % (check_path, dir_name)
                    directory_exist = True
                    try:
                        os.stat(check_path)
                    except:
                        directory_exist = False
                    if not directory_exist and dir_name:
                        os.system("mkdir %s" % check_path)
                        os.system("chmod 777 -R %s" % check_path)

                try:
                    os.stat(check_path)
                except:
                    raise UserError("Directory not available to import file.")

            local_path = "%s/%s" % (dir_path, file)

            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "sales_return",
                "operation": "import",
                "file_name": file,
                "company_id": self.env.user.company_id.id
            }
            process_log = self.env["process.log"].create(vals)
            log_files.append(process_log.name)
            if warehouse.ftp_server_id.connection_type == 'sftp':
                sftp_instance.get(file_server_path, local_path)
            else:
                try:
                    sftp_instance.cwd(warehouse.import_sale_return_res_from.path)
                    sftp_instance.retrbinary("RETR " + file, open("%s/%s" % (dir_path, file), 'wb').write)
                except Exception as e:
                    process_mismatch = True
                    process_log.note = "Something went wrong while processing import sales return : %s" % e

            try:
                if warehouse.import_sales_return_res_file_type == "excel":
                    file_data = self.import_sr_response_excel_process(local_path, process_log, warehouse)
                else:
                    file_data = self.import_sr_response_csv_process(local_path, process_log, warehouse)

                self.process_3pl_sr_pickings(file_data, process_log)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    os.remove(local_path)
                else:
                    os.remove('%s' % local_path)
                file_path = "%s/%s" % (warehouse.import_sale_return_res_from.path, file)
                if warehouse.move_processed_sale_return_file_to and warehouse.move_processed_sale_return_file_to.path:
                    archive_path = "%s/%s" % (warehouse.move_processed_sale_return_file_to.path, file)
                    sftp_instance.rename(file_path, archive_path)

            except Exception as e:
                process_mismatch = True
                process_log.note = "Something went wrong while processing import sales return : %s" % e

            mismatches = process_log.process_log_line_ids.filtered(lambda m: m.is_mismatch)
            if mismatches or process_mismatch:
                process_log.note = "Import Sales Return Process Failed"
            else:
                process_log.note = "Import Sales Return Processed Successfully!!!"

        if warehouse.is_notify_users_when_import_sales_return:
            ctx = dict(self._context)
            ctx.update({
                "email_to": ",".join(warehouse.notify_user_ids_import_sales_return.mapped("partner_id").mapped("email_formatted")),
                "language": warehouse.notify_user_ids_import_sales_return[0].lang,
                "user_name": self.env.user.name,
                "process_time": fields.Datetime.now().strftime("%d:%m:%Y:%H:%M:%S"),
                "process_log": log_files and log_files[0] or "-"
            })
            warehouse.import_sales_return_email_template_id.with_context(ctx).send_mail(warehouse.id)
        return True

    def process_3pl_sr_pickings(self, file_data, process_log):
        process_log_line_obj = self.env["process.log.line"]
        product = False
        for picking, product_data in file_data.items():
            line_skipped = True
            process_log_line = False
            try:
                if picking.state == 'draft':
                    picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                picking.move_line_ids.exists().unlink()
                for product, data in product_data.items():
                    process_log_line_domain = [
                        ("process_log_id", "=", process_log.id),
                        ("picking_id", "=", picking.id),
                        ("product_id", "=", product.id)
                    ]
                    process_log_line = process_log_line_obj.search(process_log_line_domain, order="id desc", limit=1)
                    move = picking.move_ids_without_package.filtered(lambda line: line.product_id == product)
                    if move:
                        if move.product_id and move.product_id.tracking == 'none':
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            move.quantity = data.get('quantity')
                        elif move.product_id and move.product_id.tracking == "serial":
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            if data.get('lot_id'):
                                for serial in data.get('lot_id'):
                                    self.env['stock.move.line'].create({
                                        'lot_id': serial,
                                        'quantity': 1,
                                        'product_id': move.product_id.id,
                                        'picking_id': picking.id,
                                        'move_id': move.id,})
                                # break
                        if move.product_id and move.product_id.tracking == 'lot':
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            if data.get('lot_id'):
                                self.env['stock.move.line'].create({
                                        'lot_id': data.get('lot_id'),
                                        'quantity': data.get('quantity'),
                                        'product_id': move.product_id.id,
                                        'picking_id': picking.id,
                                        'move_id': move.id,})

                        picking.tpl_status = data.get("status", "-")

                if picking.tpl_status in ['Done', 'Received']:
                    picking_sr = picking.with_context(skip_immediate=True, skip_sms=True).button_validate()
                    if isinstance(picking_sr, dict) and picking_sr.get('res_model') == 'stock.backorder.confirmation':
                        wizard_id = self.env['stock.backorder.confirmation'].with_context(picking_sr.get('context')).create({})
                        wizard_id.with_context(picking_sr.get('context')).process()
                    line_skipped = False
                    self._cr.commit()
            except Exception as e:
                if not process_log_line:
                    process_log_line_domain = [
                        ("process_log_id", "=", process_log.id),
                        ("picking_id", "=", picking.id),
                    ]
                    if product:
                        process_log_line_domain.append(("product_id", "=", product.id))
                    process_log_line = process_log_line_obj.search(process_log_line_domain, order="id desc", limit=1)
                process_log_line.write({
                    "is_mismatch": True,
                    "is_skip_line": line_skipped,
                    "message": e
                })
        return True

    def import_sr_response_from_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.is_auto_import_sales_return:
                self.import_sr_response_from_3pl(warehouse)
        return True

    def import_po_response_excel_process(self, local_path, process_log, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]
        file_data = {}
        if warehouse.ftp_server_id.connection_type == 'sftp':
            workbook = xlrd.open_workbook(local_path)
        else:
            workbook = xlrd.open_workbook('%s' % local_path)
        sheet = workbook.sheet_by_index(0)
        import_po_file = False
        for row_count in range(sheet.nrows):
            try:
                row_list = sheet.row_values(row_count, 0, sheet.ncols)
                if not import_po_file:
                    if row_list[0] != "Receipt Ref." or row_list[4] != "Internal Reference" or row_list[5] != "Product Name":
                        return {}
                import_po_file = True
                product_ref = row_list[4]
                product_barcode = row_list[6]

                if row_list[0].lower() == "receipt ref.":
                    continue
                line_skipped = True
                process_log_line = process_log_line_obj.create({
                    "process_log_id": process_log.id,
                    "is_mismatch": False,
                })

                product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                if not product:
                    product = product_obj.search([("barcode", "=", product_barcode)], limit=1)
                if not product:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Product Not Found For Line : %s" % row_list
                    })
                    continue
                process_log_line.product_id = product
                picking = self.search([("name", "=", row_list[0]), ("state", "not in", ["done", "cancel"])])
                
                if row_list[2]:
                    picking.write({'carrier_tracking_ref': row_list[2]})
                if len(row_list) != 16 or row_list[15] not in ['Done', 'Received']:
                    picking = False

                if not picking:
                    picking = self.search([("name", "=", row_list[0]), ("state", "in", ["done", "cancel"])])
                    if picking:
                        picking_state = "Done"
                        if picking.state == "cancel":
                            picking_state = "Cancel"
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "picking %s is in %s state." % (row_list[0], picking_state)
                        })
                else:
                    picking_state = "Done"
                    if picking.state == "cancel":
                        picking_state = "Cancel"
                    process_log_line.write({
                        "message": "picking %s is in %s state." % (row_list[0], picking_state)
                    })

                if not picking:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Picking Not Found For Line : %s" % row_list
                    })
                    continue

                tmp_data = file_data.get(picking, {})
                lot_id = False
                serial_num = []
                if product.tracking == 'lot' and row_list[13]:
                    lot_no = row_list[13]
                    if lot_no.is_integer():
                        lot_no = int(lot_no)
                    lot_id = self.env['stock.lot'].search([
                        ('name', '=', str(lot_no)),
                        ('product_id', '=', product.id),
                        ('company_id', '=', warehouse.company_id.id)], limit=1).id
                    if not lot_id:
                        vals = {
                            "name": str(lot_no),
                            "product_id": product.id,
                            "product_qty": int(row_list[14]),
                            "company_id": warehouse.company_id.id
                        }
                        lot_id = self.env['stock.lot'].create(vals).id

                if product.tracking == 'serial' and row_list[13]:
                    row_list_lot = str(row_list[13]).split(',')
                    if int(row_list[14]) != len(row_list_lot):
                        raise ValidationError(('Please add serial number as defined quantity'))
                    else:
                        row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                        for lot in row_list_lot_updated:
                            lot_no = self.env['stock.lot'].search([
                                ('name', '=', lot),
                                ('product_id', '=', product.id),
                                ('company_id', '=', warehouse.company_id.id)], limit=1)

                            if not lot_no:
                                vals = {
                                    "name": lot,
                                    "product_id": product.id,
                                    "product_qty": 1,
                                    "company_id": warehouse.company_id.id,
                                }
                                lot_no = self.env['stock.lot'].create(vals)
                            serial_num.append(lot_no.id)

                tmp_data.update({
                    product: {
                        "lot_id": lot_id if lot_id else serial_num,
                        "quantity": row_list[14],
                        "status": row_list[15]
                    }
                })

                file_data.update({picking: tmp_data})
                line_skipped = False

            except Exception as e:
                if product.tracking == 'serial' and row_list[13]:
                    row_list_lot = str(row_list[13]).split(',')
                    if int(row_list[14]) != len(row_list_lot):
                        process_log_line.write({
                            "is_skip_line": line_skipped,
                            "is_mismatch": True,
                            "message": "Please add serial number as defined quantity for line: %s" % row_list[13]
                        })
                else:
                    process_log_line.write({
                        "is_mismatch": True,
                        "is_skip_line": line_skipped,
                        "message": "Error While Processing Line : %s" % row_list
                    })
                continue
        return file_data

    def import_po_response_csv_process(self, local_path, process_log, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]
        file_data = {}
        try:
            local_path_open = '$%s' % local_path
            check_file = open(local_path_open, mode='r')
        except Exception as e:
            local_path_open = '%s' % local_path
        with open(local_path_open, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            import_po_file = False
            for row in csv_reader:
                try:
                    line_skipped = True
                    keys_list = list(row.keys())
                    if not import_po_file:
                        if keys_list[0] != "Picking Ref." or keys_list[4] != "Internal Reference" or keys_list[5] != "Product Name":
                            return {}
                    import_po_file = True

                    process_log_line = process_log_line_obj.create({
                        "process_log_id": process_log.id,
                        "is_mismatch": False,
                    })

                    product_ref = row.get("Internal Reference", False)
                    product_barcode = row.get("Product Barcode", False)
                    product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                    if not product:
                        product = product_obj.search([("barcode", "=", product_barcode)], limit=1)
                    if not product:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Product Not Found For Line : %s" % row
                        })
                        continue

                    if not row.get("Picking Ref.", False):
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Picking Ref Not Found In Line : %s" % row
                        })
                        continue

                    picking = self.search(
                        [("name", "=", row.get("Picking Ref.")), ("state", "not in", ["done", "cancel"])])
                    if 'Status' not in row or row.get('Status') not in ['Done', 'Received']:
                        picking = False
                    if not picking:
                        picking = self.search([("name", "=", row.get("Picking Ref.")), ("state", "in", ["done", "cancel"])])    
                        if picking:
                            picking_state = "Done"
                            if picking.state == "cancel":
                                picking_state = "Cancel"
                            process_log_line.write({
                                "is_mismatch": True,
                                "is_skip_line": line_skipped,
                                "message": "picking %s is in %s state." % (row.get("Picking Ref."), picking_state)
                            })

                    if not picking:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Picking Not Found For Line : %s" % row
                        })
                        continue

                    tmp_data = file_data.get(picking, {})
                    lot_id = False
                    serial_num = []
                    if product.tracking == 'lot' and row.get("Lot/Serial Number"):
                        lot_id = self.env['stock.lot'].search([
                            ('name', '=', row.get("Lot/Serial Number")),
                            ('product_id', '=', product.id),
                            ('company_id', '=', warehouse.company_id.id)], limit=1).id
                        if not lot_id:
                            vals = {
                                "name": row.get("Lot/Serial Number"),
                                "product_id": product.id,
                                "product_qty": eval(row.get("Done Quantity")),
                                "company_id": warehouse.company_id.id
                            }
                            lot_id = self.env['stock.lot'].create(vals).id

                    if product.tracking == 'serial' and row.get("Lot/Serial Number"):
                        row_list_lot = row.get("Lot/Serial Number").split(',')
                        if eval(row.get("Done Quantity")) != len(row_list_lot):
                            raise ValidationError(('Please add serial number as defined quantity'))
                        else:
                            row_list_lot_updated = self.get_list_serial_evaluate(row_list_lot)
                            for lot in row_list_lot_updated:
                                lot_no = self.env['stock.lot'].search([
                                    ('name', '=', lot),
                                    ('product_id', '=', product.id),
                                    ('company_id', '=', warehouse.company_id.id)], limit=1)

                                if not lot_no:
                                    vals = {
                                        "name": lot,
                                        "product_id": product.id,
                                        "product_qty": 1,
                                        "company_id": warehouse.company_id.id,
                                    }
                                    lot_no = self.env['stock.lot'].create(vals)
                                serial_num.append(lot_no.id)

                    tmp_data.update({
                        product: {
                            "lot_id": lot_id if lot_id else serial_num,
                            "quantity": row.get("Done Quantity", 0.0),
                            "status": row.get("Status", "-")
                        }
                    })

                    file_data.update({picking: tmp_data})
                    line_skipped = False
                except Exception as e:
                    if product.tracking == 'serial' and row.get("Lot/Serial Number"):
                        row_list_lot = row.get("Lot/Serial Number").split(',')
                        if eval(row.get("Done Quantity")) != len(row_list_lot):
                            process_log_line.write({
                                "is_skip_line": line_skipped,
                                "is_mismatch": True,
                                "message": "Please add serial number as defined quantity for line: %s" % row
                            })
                    else:
                        process_log_line.write({
                            "is_mismatch": True,
                            "is_skip_line": line_skipped,
                            "message": "Error While Processing Line : %s" % row
                        })
                    continue
        return file_data

    def import_po_response_from_3pl(self, warehouse):
        process_mismatch = False
        sftp_instance = warehouse.ftp_server_id.connect_to_ftp_server()
        log_files = []

        flag = False
        if (not warehouse.import_purchase_res_from.path) or (
                warehouse.ftp_server_id.connection_type == 'sftp' and not sftp_instance.isdir(
                warehouse.import_purchase_res_from.path)):
            flag = True
        if warehouse.ftp_server_id.connection_type == 'ftp':
            flag = warehouse.ftp_server_id.check_ftp_directory(sftp_instance, warehouse.import_purchase_res_from.path)
        if flag:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "purchase",
                "operation": "import",
                "company_id": self.env.user.company_id.id,
                "note": "Location not found on FTP Server : %s" % warehouse.import_purchase_res_from.path
            }

            self.env["process.log"].create(vals)
            return True

        if warehouse.ftp_server_id.connection_type == 'sftp':
            file_list = sftp_instance.listdir(warehouse.import_purchase_res_from.path)
        else:
            file_list = [name for name, facts in sftp_instance.mlsd(warehouse.import_purchase_res_from.path)]
        if len(file_list) == 0:
            raise UserError("There are no files available on the server/directory.")
        file_extension = ".xlsx"
        if warehouse.import_purchase_res_file_type == "csv":
            file_extension = ".csv"

        import_files = [] # All Import file are stored here
        exported_files = [] # All Export files are stored here 
        identity_import_files = []

        for file_name in file_list:
            import_prefix = warehouse.import_purchase_res_prefix
            if file_name.startswith(import_prefix):
                import_files.append(file_name)
            else:
                exported_files.append(file_name)

        for exported_file in exported_files:
            leangth = len(warehouse.export_purchase_prefix)
            sliced_file = exported_file[leangth:]
            export_file = ''.join((warehouse.import_purchase_res_prefix, sliced_file)) 
            export_file = export_file.rstrip(file_extension)
            identity_import_files.append(export_file)

        if len(exported_files) > 0:
            for check_file in identity_import_files:
                duplicate_file_lst = []
                for imp_files in import_files:
                    if imp_files.startswith(check_file):
                        duplicate_file_lst.append(imp_files)
                if len(duplicate_file_lst) > 1:
                    raise ValidationError(("You have duplicate '%s%s' Import Files in your directory.\n Please remove unnecessary file to continue this process.") % (check_file , file_extension))

        stock_files_to_process = []
        for file_name in file_list:
            if file_name.startswith(warehouse.import_purchase_res_prefix):
                if (warehouse.import_purchase_res_file_type == 'excel' and warehouse.export_purchase_file_type == 'excel') or (warehouse.import_purchase_res_file_type == 'excel' and warehouse.export_purchase_file_type == 'csv'):
                    if re.findall("^%s" % warehouse.import_purchase_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                        if file_name.startswith(warehouse.import_purchase_res_prefix) and file_name.endswith('.xlsx'):
                            stock_files_to_process.append(file_name)
                    else:
                        vals = {
                            "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                            "process_datetime": fields.datetime.now(),
                            "application": "purchase",
                            "file_name": "Import EXCEL File Not Found!!!!!",
                            "operation": "import",
                            "company_id": self.env.user.company_id.id,
                            "note": "Import EXCEL File Not Found!!!!!"
                        }
                        self.env["process.log"].create(vals)
                elif (warehouse.import_purchase_res_file_type == 'csv' and warehouse.export_purchase_file_type == 'csv') or (warehouse.import_purchase_res_file_type == 'csv' and warehouse.export_purchase_file_type == 'excel'):
                    if re.findall("^%s" % warehouse.import_purchase_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                        if file_name.startswith(warehouse.import_purchase_res_prefix) and file_name.endswith('.csv'):
                            stock_files_to_process.append(file_name)
                    else:
                        vals = {
                            "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                            "process_datetime": fields.datetime.now(),
                            "application": "purchase",
                            "file_name": "Import CSV File Not Found!!!!!",
                            "operation": "import",
                            "company_id": self.env.user.company_id.id,
                            "note": "Import CSV File Not Found!!!!!"
                        }
                        self.env["process.log"].create(vals)

        for file in stock_files_to_process:

            file_server_path = "%s/%s" % (warehouse.import_purchase_res_from.path, file)
            if not warehouse.import_ftp_files_to:
                raise UserError("Import directory path not configured in warehouse.")

            dir_path = warehouse.import_ftp_files_to

            try:
                os.stat(dir_path)
            except:
                check_path = ""
                for dir_name in dir_path.split('/'):
                    if dir_name == "":
                        continue
                    check_path = "%s/%s" % (check_path, dir_name)
                    directory_exist = True
                    try:
                        os.stat(check_path)
                    except:
                        directory_exist = False
                    if not directory_exist and dir_name:
                        os.system("mkdir %s" % check_path)
                        os.system("chmod 777 -R %s" % check_path)

                try:
                    os.stat(check_path)
                except:
                    raise UserError("Directory not available to import file.")

            local_path = "%s/%s" % (dir_path, file)
            os.system("chmod 777 -R %s" % dir_path)
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "purchase",
                "operation": "import",
                "file_name": file,
                "company_id": self.env.user.company_id.id
            }
            process_log = self.env["process.log"].create(vals)
            log_files.append(process_log.name)
            if warehouse.ftp_server_id.connection_type == 'sftp':
                try:
                    sftp_instance.get(file_server_path, '$%s' % local_path)
                except Exception as e:
                    sftp_instance.get(file_server_path, '%s' % local_path)
            else:
                try:
                    sftp_instance.cwd(warehouse.import_purchase_res_from.path)
                    sftp_instance.retrbinary("RETR " + file, open("%s/%s" % (dir_path, file), 'wb').write)
                except Exception as e:
                    process_mismatch = True
                    process_log.note = "Something went wrong while processing import purchase : %s" % e
            try:
                local_path = "%s/%s" % (dir_path, file)
                if warehouse.import_purchase_res_file_type == "excel":
                    file_data = self.import_po_response_excel_process(local_path, process_log, warehouse)
                else:
                    file_data = self.import_po_response_csv_process(local_path, process_log, warehouse)
                self.process_3pl_po_pickings(file_data, process_log)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    os.remove(local_path)
                else:
                    os.remove('%s' % local_path)
                file_path = "%s/%s" % (warehouse.import_purchase_res_from.path, file)
                if warehouse.move_processed_purchase_file_to and warehouse.move_processed_purchase_file_to.path:
                    archive_path = "%s/%s" % (warehouse.move_processed_purchase_file_to.path, file)
                    sftp_instance.rename(file_path, archive_path)

            except Exception as e:
                process_mismatch = True
                process_log.note = "Something went wrong while processing import purchase : %s" % e

            mismatches = process_log.process_log_line_ids.filtered(lambda m: m.is_mismatch)
            if not mismatches and not process_mismatch:
                process_log.note = "Import Purchase Processed Successfully!!!"

            if warehouse.is_notify_users_when_import_purchase:
                ctx = dict(self._context)
                ctx.update({
                    "email_to": ",".join(warehouse.notify_user_ids_import_purchase.mapped("partner_id").mapped("email_formatted")),
                    "language": warehouse.notify_user_ids_import_purchase[0].lang,
                    "user_name": self.env.user.name,
                    "process_time": fields.Datetime.now().strftime("%d:%m:%Y:%H:%M:%S"),
                    "process_log": log_files and log_files[0] or "-"
                })
                warehouse.import_purchase_email_template_id.with_context(ctx).send_mail(warehouse.id)
        return True

    def process_3pl_po_pickings(self, file_data, process_log):
        process_log_line_obj = self.env["process.log.line"]
        product = False
        for picking, product_data in file_data.items():
            line_skipped = True
            process_log_line = False
            try:
                if picking.state == 'draft':
                    picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                picking.move_line_ids.exists().unlink()
                for product, data in product_data.items():
                    process_log_line_domain = [
                        ("process_log_id", "=", process_log.id),
                        ("picking_id", "=", picking.id),
                        ("product_id", "=", product.id)
                    ]
                    process_log_line = process_log_line_obj.search(process_log_line_domain, order="id desc", limit=1)
                    move = picking.move_ids_without_package.filtered(lambda line: line.product_id == product)
                    if move:
                        if move.product_id and move.product_id.tracking == 'none':
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            move.quantity = data.get('quantity')
                        elif move.product_id and move.product_id.tracking == 'lot':
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            if data.get('lot_id'):
                                self.env['stock.move.line'].create({
                                        'lot_id': data.get('lot_id'),
                                        'quantity': data.get('quantity'),
                                        'product_id': move.product_id.id,
                                        'picking_id': picking.id,
                                        'move_id': move.id,})
                        elif move.product_id and move.product_id.tracking == 'serial':
                            if move.move_line_ids.exists():
                                move.move_line_ids.exists().unlink()
                            for serial in data.get('lot_id'):
                                self.env['stock.move.line'].create({
                                        'lot_id': serial,
                                        'quantity': 1,
                                        'product_id': move.product_id.id,
                                        'picking_id': picking.id,
                                        'move_id': move.id,})

                        picking.tpl_status = data.get("status", "-")
                if picking.tpl_status in ['Done', 'Received']:
                    picking_po = picking.with_context(skip_immediate=True, skip_sms=True).button_validate()
                    if isinstance(picking_po, dict) and picking_po.get('res_model') == 'stock.backorder.confirmation':
                        wizard_id = self.env['stock.backorder.confirmation'].with_context(picking_po.get('context')).create({})
                        wizard_id.with_context(picking_po.get('context')).process()
                    line_skipped = False
                    self._cr.commit()
            except Exception as e:
                if not process_log_line:
                    process_log_line_domain = [
                        ("process_log_id", "=", process_log.id),
                        ("picking_id", "=", picking.id),
                    ]
                    if product:
                        process_log_line_domain.append(("product_id", "=", product.id))
                    process_log_line = process_log_line_obj.search(process_log_line_domain, order="id desc", limit=1)
                process_log_line.write({
                    "is_mismatch": True,
                    "is_skip_line": line_skipped,
                    "message": e
                })
        return True

    def import_po_response_from_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.is_auto_import_purchase_res:
                if warehouse.ftp_server_id.state == "confirmed" and warehouse.is_auto_import_purchase_res:
                    vals = {
                        "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                        "process_datetime": fields.datetime.now(),
                        "application": "purchase",
                        "operation": "import",
                        "company_id": warehouse.company_id.id
                    }
                    process_log = self.env["process.log"].create(vals)
                    self.import_po_response_from_3pl(warehouse)

        return True

    def mark_exported_not_exported(self):
        for record in self:
            record.is_exported = not record.is_exported


class StockMove(models.Model):
    _inherit = "stock.move"

    is_exported = fields.Boolean("Exported", default=False, copy=False, help="True if picking is exported to 3PL.")
