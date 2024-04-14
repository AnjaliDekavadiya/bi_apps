# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re
import xlrd
import csv
import os


class StockInventory(models.Model):
    _inherit = "stock.quant"

    def import_stock_from_3pl(self, warehouse):
        product_obj = self.env["product.product"]
        process_log_line_obj = self.env["process.log.line"]

        sftp_instance = warehouse.ftp_server_id.connect_to_ftp_server()
        inventory_adjustment = False
        log_file_list = []

        flag = False
        if (not warehouse.import_stock_file_from.path) or (warehouse.ftp_server_id.connection_type == 'sftp' and not sftp_instance.isdir(warehouse.import_stock_file_from.path)):
            flag = True
        if warehouse.ftp_server_id.connection_type == 'ftp':
            flag = warehouse.ftp_server_id.check_ftp_directory(sftp_instance, warehouse.import_stock_file_from.path)
        if flag:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "stock",
                "operation": "import",
                "company_id": self.env.user.company_id.id,
                "note": "Location not found on FTP Server : %s" % warehouse.import_stock_file_from.path
            }

            self.env["process.log"].create(vals)
            return True

        if warehouse.ftp_server_id.connection_type == 'sftp':
            file_list = sftp_instance.listdir(warehouse.import_stock_file_from.path)
        else:
            file_list = [name for name, facts in sftp_instance.mlsd(warehouse.import_stock_file_from.path)]
        file_extension = ".xlsx"
        if warehouse.import_stock_file_type == "csv":
            file_extension = ".csv"

        stock_files_to_process = []
        for file_name in file_list:
            if re.findall("^%s" % warehouse.import_stock_res_prefix, file_name) and re.findall("%s$" % file_extension, file_name):
                stock_files_to_process.append(file_name)
        for file in stock_files_to_process:
            file_server_path = "%s/%s" % (warehouse.import_stock_file_from.path, file)
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
                except Exception as e:
                    raise Warning(_("Directory is not available to import file. %s" % e))

            local_path = "%s/%s" % (dir_path, file)
            os.system("chmod 777 -R %s" % dir_path)
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "stock",
                "operation": "import",
                "file_name": file,
                "company_id": self.env.user.company_id.id
            }

            process_log = self.env["process.log"].create(vals)
            log_file_list.append(process_log.name)
            if warehouse.ftp_server_id.connection_type == 'sftp':
                try:
                    sftp_instance.get(file_server_path, '%s' % local_path)
                except Exception as e:
                    sftp_instance.get(file_server_path, '%s' % local_path)
            else:
                try:
                    sftp_instance.cwd(warehouse.import_stock_file_from.path)
                    sftp_instance.retrbinary("RETR " + file, open("%s/%s" % (dir_path, file), 'wb').write)
                except Exception as e:
                    process_log.note = "Something went wrong while processing import stock : %s" % e

            try:
                line_list = []
                line_id_exist = False
                if warehouse.import_stock_file_type == "excel":
                    if warehouse.ftp_server_id.connection_type == 'sftp':
                        workbook = xlrd.open_workbook(local_path)
                    else:
                        workbook = xlrd.open_workbook("%s/%s" % (dir_path, file))
                    sheet = workbook.sheet_by_index(0)
                    import_stock_file = False
                    for row_count in range(sheet.nrows):
                        try:
                            line_skipped = True
                            process_log_line_vals = {
                                "process_log_id": process_log.id,
                                "is_mismatch": False,
                            }
                            process_log_line = process_log_line_obj.create(process_log_line_vals)
                            row_list = sheet.row_values(row_count, 0, sheet.ncols)

                            if not import_stock_file:
                                if row_list[0] != "Internal Reference" or row_list[1] != "Name" or row_list[2] != "Barcode" or row_list[3] != "Product Category" or row_list[4] != "Cost Price" or row_list[5] != "Sale Price" or row_list[6] != "Weight" or row_list[7] != "Volume" or row_list[8] != "UOM" or row_list[9] != "Quantity":
                                    return {}
                            import_stock_file = True

                            if row_list[0].lower() == "internal reference":
                                continue
                            product_ref = row_list[0]
                            product_barcode = row_list[2]

                            product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                            if not product:
                                product = product_obj.search([("barcode", "=", product_barcode)])
                            process_log_line.write({
                                "product_id": product.id,
                                "file_qty": float(row_list[9]),
                                "message": "Stock of Product %s Imported Successfully" % product.display_name
                            })
                            if not product:
                                process_log_line.write({
                                    "message": "Product not found for line %s" % row_list,
                                    "is_mismatch": True,
                                    "is_skip_line": True
                                })
                                continue
                            product_quant = self._get_available_quantity(product_id=product, location_id=warehouse.lot_stock_id, lot_id=None, package_id=None, owner_id=None, strict=None, allow_negative=None)
                            if product.tracking == "none":
                                inventory_lines_vals = {
                                    'product_id': product.id,
                                    'product_uom_id': product.uom_id.id,
                                    'inventory_quantity': row_list[9],
                                    'quantity': product_quant,
                                    'location_id': warehouse.lot_stock_id.id,
                                }
                                line_list.append((0, 0, inventory_lines_vals))
                                line_id_exist = True

                            elif product.tracking == "lot":
                                lot_obj = self.env["stock.lot"]
                                fields_list = [field for field, value in lot_obj.fields_get().items()]
                                default_values = lot_obj.default_get(fields_list)
                                default_values.update({
                                    "product_id": product.id,
                                    "company_id": warehouse.company_id.id
                                })
                                lot_id = lot_obj.create(default_values)
                                inventory_lines_vals = {
                                    'product_id': product.id,
                                    'product_uom_id': product.uom_id.id,
                                    'inventory_quantity': row_list[9],
                                    'quantity': product_quant,
                                    'location_id': warehouse.lot_stock_id.id,
                                    'prod_lot_id': lot_id.id
                                }
                                line_list.append((0, 0, inventory_lines_vals))
                                line_id_exist = True
                            elif product.tracking == "serial":
                                lot_obj = self.env["stock.lot"]
                                for index in range(int(row_list[9])):
                                    fields_list = [field for field, value in lot_obj.fields_get().items()]
                                    default_values = lot_obj.default_get(fields_list)
                                    default_values.update({
                                        "product_id": product.id,
                                        "company_id": warehouse.company_id.id
                                    })
                                    lot_id = lot_obj.create(default_values)
                                    inventory_lines_vals = {
                                        'product_id': product.id,
                                        'product_uom_id': product.uom_id.id,
                                        'inventory_quantity': 1,
                                        'quantity': 1,
                                        'location_id': warehouse.lot_stock_id.id,
                                        'prod_lot_id': lot_id.id
                                    }

                                    line_list.append((0, 0, inventory_lines_vals))
                                    line_id_exist = True
                            line_skipped = False
                        except Exception as e:
                            message = "Facing issue while importing stock : %s" % e
                            process_log_line.write({
                                "message": message,
                                "is_mismatch": True,
                                "is_skip_line": line_skipped
                            })
                else:
                    if warehouse.ftp_server_id.connection_type == 'sftp':
                        try:
                            local_path_open = '%s' % local_path
                            file_open = open(local_path_open, mode='r')
                        except:
                            local_path_open = '%s' % local_path
                    else:
                        local_path_open = "%s/%s" % (dir_path, file)
                    with open(local_path_open, mode='r') as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        import_stock_file = False
                        for row in csv_reader:
                            try:
                                line_skipped = True

                                keys_list = list(row.keys())
                                if not import_stock_file:
                                    if keys_list[0] != "Internal Reference" or keys_list[1] != "Name" or keys_list[2] != "Barcode" or keys_list[3] != "Product Category" or keys_list[4] != "Cost Price" or keys_list[5] != "Sale Price" or keys_list[6] != "Weight" or keys_list[7] != "Volume" or keys_list[8] != "UOM" or keys_list[9] != "Quantity":
                                        return {}
                                import_stock_file = True

                                process_log_line_vals = {
                                    "process_log_id": process_log.id,
                                    "is_mismatch": False,
                                }
                                process_log_line = process_log_line_obj.create(process_log_line_vals)
                                product_ref = row.get("Internal Reference", False)
                                product_barcode = row.get("Product Barcode", False)

                                product = product_obj.search([("default_code", "=", product_ref)], limit=1)
                                inventory_adjustment_vals = {
                                    'product_id': product.id,
                                    'product_uom_id': product.uom_id.id,
                                    'location_id': warehouse.lot_stock_id.id,
                                    'inventory_quantity': keys_list[9]
                                }
                                if not product:
                                    product = product_obj.search([("barcode", "=", product_barcode)])
                                if not product:
                                    process_log_line.write({
                                        "message": "Product not found for line %s" % row,
                                        "is_mismatch": True,
                                        "is_skip_line": True
                                    })
                                    continue
                                process_log_line.write({
                                    "product_id": product.id,
                                    "file_qty": row.get("Quantity", 0.0),
                                    "message": "Stock of Product %s Imported Successfully" % product.display_name
                                })
                                product_quant = self._get_available_quantity(product_id=product, location_id=warehouse.lot_stock_id, lot_id=None, package_id=None, owner_id=None, strict=None, allow_negative=None)
                                if product.tracking == "none":
                                    inventory_lines_vals = {
                                        'product_id': product.id,
                                        'product_uom_id': product.uom_id.id,
                                        'quantity': product_quant,
                                        'inventory_quantity': float(row.get("Quantity")),
                                        'location_id': warehouse.lot_stock_id.id,
                                    }
                                    line_list.append((0, 0, inventory_lines_vals))
                                    line_id_exist = True

                                elif product.tracking == "lot":
                                    lot_obj = self.env["stock.lot"]

                                    fields_list = [field for field, value in lot_obj.fields_get().items()]
                                    default_values = lot_obj.default_get(fields_list)
                                    default_values.update({
                                        "product_id": product.id,
                                        "company_id": warehouse.company_id.id
                                    })
                                    lot_id = lot_obj.create(default_values)

                                    inventory_lines_vals = {
                                        'product_id': product.id,
                                        'product_uom_id': product.uom_id.id,
                                        'inventory_quantity': float(row.get("Quantity")),
                                        'location_id': warehouse.lot_stock_id.id,
                                        'quantity': product_quant,
                                        'prod_lot_id': lot_id.id
                                    }

                                    line_list.append((0, 0, inventory_lines_vals))
                                    line_id_exist = True

                                elif product.tracking == "serial":
                                    lot_obj = self.env["stock.lot"]

                                    for index in range(int(row.get("Quantity"))):
                                        fields_list = [field for field, value in lot_obj.fields_get().items()]
                                        default_values = lot_obj.default_get(fields_list)
                                        default_values.update({
                                            "product_id": product.id,
                                            "company_id": warehouse.company_id.id
                                        })
                                        lot_id = lot_obj.create(default_values)

                                        inventory_lines_vals = {
                                            'product_id': product.id,
                                            'product_uom_id': product.uom_id.id,
                                            'inventory_quantity': 1,
                                            'quantity': 1,
                                            'location_id': warehouse.lot_stock_id.id,
                                            'prod_lot_id': lot_id.id
                                        }

                                        line_list.append((0, 0, inventory_lines_vals))
                                        line_id_exist = True
                                line_skipped = False
                            except Exception as e:
                                message = "Facing issue while importing stock : %s" % e
                                process_log_line.write({
                                    "message": message,
                                    "is_mismatch": True,
                                    "is_skip_line": line_skipped
                                })
                if line_list and line_id_exist:
                    for rec in line_list:
                        find = self.search([("product_id", "=", rec[2].get('product_id')), ("location_id", "=", rec[-1].get('location_id'))])
                        inventory_adjustment_vals = {
                            'product_id': rec[2].get('product_id'),
                            'product_uom_id': rec[2].get('product_uom_id'),
                            'inventory_quantity': rec[2].get('inventory_quantity'),
                            'quantity': rec[2].get('quantity'),
                            'location_id': rec[2].get('location_id')}
                        if 'prod_lot_id' in rec[2]:
                            inventory_adjustment_vals.update({'lot_id': rec[2].get('prod_lot_id'),})
                        if find and find.product_id and find.product_id.tracking == 'serial':
                            find = False
                        if find:
                            inventory_adjustment = find.write(inventory_adjustment_vals)
                            if warehouse.is_auto_validate_inventory:
                                find.action_apply_inventory()
                        else:
                            inventory_adjustment = self.create(inventory_adjustment_vals)
                            if warehouse.is_auto_validate_inventory:
                                inventory_adjustment.action_apply_inventory()

                    if warehouse.ftp_server_id.connection_type == 'sftp':
                        os.remove(local_path)
                    else:
                        os.remove('%s' % local_path)
                    file_path = "%s/%s" % (warehouse.import_stock_file_from.path, file)
                    if warehouse.move_processed_stock_file_to and warehouse.move_processed_stock_file_to.path:
                        archive_path = "%s/%s" % (warehouse.move_processed_stock_file_to.path, file)
                        sftp_instance.rename(file_path, archive_path)

                    if inventory_adjustment and warehouse.is_notify_users_when_import_stock:
                        ctx = dict(self._context)
                        ctx.update({
                            "email_to": ",".join(warehouse.notify_user_ids_import_stock.mapped("partner_id").mapped("email_formatted")),
                            "language": warehouse.notify_user_ids_import_stock[0].lang,
                            "user_name": self.env.user.name,
                            "process_time": fields.Datetime.now(),
                            "process_log": ",".join(log_file_list)
                        })
                        warehouse.import_stock_email_template_id.with_context(ctx).send_mail(warehouse.id)
                    process_log.note = "Process Has Been Completed Successfully!!!"
            except Exception as e:
                process_log.note = "Something went wrong while processing import stock : %s" % e
        return True

    def import_stock_from_3pl_cron(self):
        warehouses = self.env["stock.warehouse"].search([("is_3pl_warehouse", "=", True)])

        for warehouse in warehouses:
            if warehouse.is_auto_import_stock:
                self.import_stock_from_3pl(warehouse)
