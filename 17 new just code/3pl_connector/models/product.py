# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import xlsxwriter
import tempfile
import csv


class ProductProduct(models.Model):
    _inherit = "product.product"

    def create_excel_file_for_3pl(self, warehouse, process_log):
        try:
            process_log_line_obj = self.env["process.log.line"]
            if not self:
                raise UserError(_("Data not available for export products. Select at least 1 product to export."))
            temp_location = tempfile.mkstemp()[1]
            workbook = xlsxwriter.Workbook(temp_location + '.xlsx')

            cell_data_format = workbook.add_format({
                'align': 'left', 'border': 1, 'size': 10})
            cell_amount_format = workbook.add_format({
                'align': 'right', 'border': 1, 'size': 10})

            try:

                worksheet = workbook.add_worksheet("product")
                row, column = 0, 0

                worksheet.set_column('A:A', 20)
                worksheet.set_column('B:B', 20)
                worksheet.set_column('C:C', 20)
                worksheet.set_column('D:D', 15)
                worksheet.set_column('E:E', 15)
                worksheet.set_column('F:F', 15)
                worksheet.set_column('G:G', 15)
                worksheet.set_column('H:H', 15)
                worksheet.set_column('I:I', 15)
                worksheet.set_column('J:J', 15)

                # Report Headers
                worksheet.write(row, 0, 'Internal Reference', cell_data_format)
                worksheet.write(row, 1, 'Name', cell_data_format)
                worksheet.write(row, 2, 'Barcode', cell_data_format)
                worksheet.write(row, 3, 'Product Category', cell_data_format)
                worksheet.write(row, 4, 'Cost Price', cell_data_format)
                worksheet.write(row, 5, 'Sale Price', cell_data_format)
                worksheet.write(row, 6, 'Weight', cell_data_format)
                worksheet.write(row, 7, 'Volume', cell_data_format)
                worksheet.write(row, 8, 'UOM', cell_data_format)
                worksheet.write(row, 9, 'Quantity', cell_data_format)

                row += 1

                for product in self:
                    try:
                        line_skipped = True
                        process_log_line_vals = {
                            "process_log_id": process_log.id,
                            "product_id": product.id,
                            "is_mismatch": False,
                            "message": "Product %s Exported Successfully" % product.display_name
                        }
                        process_log_line = process_log_line_obj.create(process_log_line_vals)
                        stock_quant_obj = self.env['stock.quant']
                        product_quant = stock_quant_obj._get_available_quantity(product_id=product, 
                                                                    location_id=warehouse.lot_stock_id, 
                                                                    lot_id=None, package_id=None, 
                                                                    owner_id=None, strict=None, allow_negative=None)
                        # Product Details
                        worksheet.write(row, 0, product.default_code, cell_data_format)
                        worksheet.write(row, 1, product.display_name, cell_data_format)
                        worksheet.write(row, 2, product.barcode, cell_data_format)
                        worksheet.write(row, 3, product.categ_id.name)
                        worksheet.write(row, 4, product.standard_price, cell_amount_format)
                        worksheet.write(row, 5, product.list_price, cell_amount_format)
                        worksheet.write(row, 6, product.weight, cell_amount_format)
                        worksheet.write(row, 7, product.volume, cell_amount_format)
                        worksheet.write(row, 8, product.uom_id.name, cell_data_format)
                        worksheet.write(row, 9, product_quant, cell_amount_format)
                        
                        row += 1
                        line_skipped = False
                    except Exception as e:
                        message = "Facing issue while exporting product : %s" % e
                        process_log_line.write({
                            "message": message,
                            "is_mismatch": True,
                            "is_skip_line": line_skipped
                        })

            except Exception as e:
                process_log.note = "Facing issue in export products process : %s" % e
            workbook.close()
            fp = open(temp_location + '.xlsx', 'rb')
            file_name = '%sexport_%s.xlsx' % (warehouse.export_product_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
            process_log.file_name = file_name
            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_product_to.path, file_name)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(fp, dest_path)
                else:
                    sftp_instance.storbinary(f'STOR {file_name}', fp)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export products process : %s" % e

            return True
        except Exception as e:
            process_log.note = "Facing issue in export products process : %s" % e

    def create_csv_file_for_3pl(self, warehouse, process_log):
        file_name = '%sexport_%s.csv' % (warehouse.export_product_prefix, fields.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
        process_log.file_name = file_name
        process_log_line_obj = self.env["process.log.line"]
        with open(file_name, 'w+') as csvfile:
            header_names = ["Internal Reference",
                            "Name",
                            "Barcode",
                            "Product Category",
                            "Cost Price",
                            "Sale Price",
                            "Weight",
                            "Volume",
                            "UOM",
                            "Quantity"]
            writer = csv.DictWriter(csvfile, fieldnames=header_names)

            writer.writeheader()
            for product in self:
                line_skipped = True
                process_log_line_vals = {
                    "process_log_id": process_log.id,
                    "product_id": product.id,
                    "is_mismatch": False,
                    "message": "Product %s Exported Successfully" % product.display_name
                }
                process_log_line = process_log_line_obj.create(process_log_line_vals)
                stock_quant_obj = self.env['stock.quant']
                product_quant = stock_quant_obj._get_available_quantity(product_id=product, 
                                                            location_id=warehouse.lot_stock_id, 
                                                            lot_id=None, package_id=None, 
                                                            owner_id=None, strict=None, allow_negative=None)
                try:
                    product_data = {
                        "Internal Reference": product.default_code,
                        "Name": product.display_name,
                        "Product Category": product.categ_id.name,
                        "Barcode": product.barcode,
                        "Cost Price": product.standard_price,
                        "Sale Price": product.list_price,
                        "Weight": product.weight,
                        "Volume": product.volume,
                        "UOM": product.uom_id.name,
                        "Quantity": product_quant,
                    }
                    writer.writerow(product_data)
                    line_skipped = False
                except Exception as e:
                    message = "Facing issue while exporting product : %s" % e
                    process_log_line.write({
                        "message": message,
                        "is_mismatch": True,
                        "is_skip_line": line_skipped
                    })

            try:
                sftp_server = warehouse.ftp_server_id.state == "confirmed" and warehouse.ftp_server_id or False
                sftp_instance = sftp_server.connect_to_ftp_server()
                dest_path = "%s/%s" % (warehouse.export_product_to.path, file_name)
                csvfile.seek(0)
                sftp_server.check_update_path_directory(sftp_instance, dest_path)
                if warehouse.ftp_server_id.connection_type == 'sftp':
                    sftp_instance.putfo(csvfile, dest_path)
                else:
                    with open(file_name, 'rb') as csvfile:
                        sftp_instance.storbinary(f'STOR {file_name}', csvfile)
                process_log.note = "The process has been completed Successfully!!!"
            except Exception as e:
                process_log.note = "Facing issue in export products process : %s" % e

            return True

    def export_products_to_3pl(self, warehouse, process_log):
        products = self
        if not products:
            export_products_domain = [
                ("create_date", ">", warehouse.last_export_product_datetime)
            ]
            products = self.search(export_products_domain)
        if warehouse.export_product_file_type == "excel":
            products.create_excel_file_for_3pl(warehouse, process_log)
        else:
            products.create_csv_file_for_3pl(warehouse, process_log)

        warehouse.last_export_product_datetime = fields.datetime.now()

        if warehouse.is_notify_users_when_export_products:
            ctx = dict(self._context)
            ctx.update({
                "email_to": ",".join(warehouse.notify_user_ids_export_products.mapped("partner_id").mapped("email_formatted")),
                "language": warehouse.notify_user_ids_export_products[0].lang,
                "user_name": self.env.user.name,
                "process_time": process_log.process_datetime.strftime("%d:%m:%Y:%H:%M:%S"),
                "process_log": process_log.name
            })
            warehouse.export_product_email_template_id.with_context(ctx).send_mail(warehouse.id)

        return True

    def export_products_to_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])
        for warehouse in warehouses:
            if warehouse.ftp_server_id.state == "confirmed" and warehouse.is_auto_export_products:
                vals = {
                    "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                    "process_datetime": fields.datetime.now(),
                    "application": "product",
                    "operation": "export",
                }
                process_log = self.env["process.log"].create(vals)
                self.export_products_to_3pl(warehouse, process_log)
        return True
