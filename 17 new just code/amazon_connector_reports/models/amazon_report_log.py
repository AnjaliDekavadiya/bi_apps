import base64
import csv
import datetime
import json
import logging
import time
import zipfile
from io import StringIO, BytesIO
from xlsxwriter.workbook import Workbook

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.sale_amazon import utils as amazon_utils

_logger = logging.getLogger(__name__)


SUPPORTED_PATHS = (
    "[Content_Types].xml",
    "xl/sharedStrings.xml",
    "xl/styles.xml",
    "xl/workbook.xml",
    "_rels/",
    "xl/_rels",
    "xl/charts/",
    "xl/drawings/",
    "xl/externalLinks/",
    "xl/pivotTables/",
    "xl/tables/",
    "xl/theme/",
    "xl/worksheets/"
)


class AmazonReportLog(models.Model):
    _inherit = 'amazon.report.log'

    parent_id = fields.Many2one(
        comodel_name='amazon.report.log',
        string="Parent Report",
        copy=False,
    )
    child_ids = fields.One2many(
        comodel_name='amazon.report.log',
        inverse_name='parent_id',
        string="Child Reports",
        copy=False,
    )
    report_lines_count = fields.Integer(
        string="Report Lines Count",
        compute="_compute_report_lines_count",
    )
    spreadsheet_id = fields.Many2one("documents.document", string="Spreadsheet")
    statement_id = fields.Many2one("account.bank.statement", string="Statement")


    def _compute_report_lines_count(self):
        for report in self:
            if not report.report_type_id.model_id:
                report.report_lines_count = 0
            else:
                report.report_lines_count = self.env[report.report_type_id.model_id.model].\
                    search_count([('x_report_log_id', '=', report.id)])

    def request_report_list(self):
        amazon_utils.refresh_aws_credentials(self.mapped('account_id'))
        amazon_utils.ensure_account_is_set_up(self.mapped('account_id'))
        marketplace_env = self.env['amazon.marketplace']
        for report in self:
            report_list = False
            if (not report.account_id or not report.report_type_id):
                continue
            try:
                date_from = self.report_date_from.isoformat(sep='T') \
                    if self.report_date_from else False
                date_to = self.report_date_to.isoformat(sep='T') \
                    if self.report_date_to else False
                report_list = amazon_utils.get_report_list(
                    report.account_id,
                    report.report_type_id.technical_name,
                    start_date=date_from,
                    end_date=date_to,
                    marketplace_ids=report.amz_marketplace_ids.mapped('api_ref')
                    if report.amz_marketplace_ids else [],
                )
            except amazon_utils.AmazonRateLimitError:
                _logger.info(
                    "Rate limit reached while creating report to Amazon with type: %s",
                    report.report_type_id.technical_name
                )
                time.sleep(2)
            except Exception as e:
                _logger.info(
                    "Error when sending report to Amazon, ID: %s\n%s", report_list, str(e)
                )
                continue
            report.write({
                # 'report_id': report_list,
                'requested_date': fields.Datetime.now(),
                'state': 'DONE',
            })
            vals_list = []
            for report_id in report_list:
                marketplaces = marketplace_env.search([
                    ('api_ref', 'in', report_id["marketplaceIds"])
                ])
                requested_date = report_id["processingStartTime"].replace('T', ' ')[:19]
                start_date = report_id["dataStartTime"].replace('T', ' ')[:19]
                end_date = report_id["dataEndTime"].replace('T', ' ')[:19]
                vals_list.append({
                    "parent_id": report.id,
                    'account_id': report.account_id.id,
                    'amz_marketplace_ids': [(6, 0, marketplaces.ids)],
                    'report_type_id': report.report_type_id.id,
                    'report_id': report_id["reportId"],
                    'report_document_id': report_id["reportDocumentId"],
                    'requested_date': requested_date,
                    'report_date_from': start_date,
                    'report_date_to': end_date,
                    'state': report_id["processingStatus"]
                })
            self.create(vals_list)
            time.sleep(0.2)

    def create_odoo_report_lines(self):
        self.ensure_one()
        if not self.report_file:
            raise UserError("Please request a report file from Amazon!")
        if not self.report_type_id.model_id:
            self.report_type_id.generate_model_for_report_type()
        report_line_env = self.env[self.report_type_id.model_id.model]
        existing_lines = report_line_env
        if self.report_type_id.is_only_update:
            existing_lines = report_line_env.search([
                ('x_report_log_id.report_type_id', '=', self.report_type_id.id)
            ], order="sequence ASC")
        else:
            report_line_env.search([('x_report_log_id', '=', self.id)]).unlink()

        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")
        line_ids = []
        vals_list = []
        rows_count = 0
        for index, row in enumerate(reader):
            rows_count += 1
            vals = {}
            for column in self.report_type_id.report_field_ids:
                if not column.field_id or column.name not in reader.fieldnames:
                    continue
                vals[column.field_id.name] = row[column.name]
            vals["x_report_log_id"] = self.id

            if existing_lines and index < len(existing_lines):
                # Means report type is for update only and still has enough
                # records for update
                existing_lines[index].write(vals)
                line_ids.append(existing_lines[index].id)
            else:
                vals_list.append(vals)
        if rows_count < len(existing_lines):
            # Means report type is for update only and has more records than
            # the new report file
            existing_lines[rows_count:].unlink()

        line_ids += report_line_env.create(vals_list).ids
        self.report_type_id.create_update_tree_view_for_report_lines()
        return {
            "type": "ir.actions.act_window",
            "name": "Report Lines",
            "res_model": self.report_type_id.model_id.model,
            "view_mode": "tree",
            "domain": [("id", "in", line_ids)],
        }

    def button_view_report_lines(self):
        self.ensure_one()
        self.report_type_id.create_update_tree_view_for_report_lines()
        return {
            "type": "ir.actions.act_window",
            "name": "Report Lines",
            "res_model": self.report_type_id.model_id.model,
            "view_mode": "tree",
            "domain": [("x_report_log_id", "=", self.id)],
        }

    @api.model
    def update_spreadsheet_json_content(self, file):
        unzipped_size = 0
        with zipfile.ZipFile(file) as input_zip:
            if len(input_zip.infolist()) > 1000:
                raise UserError(_("The xlsx file is too big"))

            if not "[Content_Types].xml" in input_zip.namelist() or\
                not any(name.startswith("xl/") for name in input_zip.namelist()):
                raise UserError(_("The xlsx file is corrupted"))

            unzipped = {}
            for info in input_zip.infolist():
                if not info.filename.endswith((".xml", ".xml.rels")) or\
                    not info.filename.startswith(SUPPORTED_PATHS):
                    # Don't extract files others than xmls or unsupported xmls
                    continue

                unzipped_size += info.file_size
                if(unzipped_size > 50 * 1000 * 1000): # 50MB
                    raise UserError(_("The xlsx file is too big"))

                unzipped[info.filename] = input_zip.read(info.filename).decode()

            return unzipped

    def convert_report_to_document(self):
        output = BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.reader(imp_file, delimiter="\t")
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
        workbook.close()
        if self.spreadsheet_id:
            old_spreadsheet = json.loads(self.spreadsheet_id.raw)
            new_spreadsheet =  self.update_spreadsheet_json_content(output)
            old_spreadsheet["xl/sharedStrings.xml"] = new_spreadsheet["xl/sharedStrings.xml"]
            self.spreadsheet_id.write({
                "handler": "spreadsheet",
                "mimetype": "application/o-spreadsheet",
                "raw": json.dumps(old_spreadsheet)
            })
            spreadsheet_id = self.spreadsheet_id.id
        else:
            document = self.env["documents.document"].create({
                "folder_id": self.env.ref("documents_spreadsheet.documents_spreadsheet_folder").id,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "name": self.report_filename + '.xlsx',
                "raw": output.getvalue(),
            })
            spreadsheet_id = document.clone_xlsx_into_spreadsheet()
            document.unlink()
            self.write({"spreadsheet_id": spreadsheet_id})
        return {
            "type": "ir.actions.client",
            "tag": "action_open_spreadsheet",
            "params": {
                "spreadsheet_id": spreadsheet_id,
            }
        }

    def process_report_GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2(self):
        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")
        sync_log_env = self.env["amazon.synchronization.log"]
        so_lines = self.env["sale.order.line"]
        marketplace_env = self.env["amazon.marketplace"]
        statement_data = next(reader)
        statement_lines_data = {}
        order_amount_dict = {}
        other_transactions_data = []
        existing_report = self.search([
            ("report_id", "!=", False),
            ("report_id", "=", self.report_id),
            ("statement_id", "!=", False),
        ])
        if existing_report:
            raise UserError("This report is already processed!\nReport Odoo ID: %s" % existing_report.id)
        marketplace_name = self.amz_marketplace_ids.mapped("name")
        journal_marketplace = self.amz_marketplace_ids.mapped("journal_id")
        for row in reader:
            if (row["marketplace-name"] and row["marketplace-name"] != "Non-Amazon" and 
                (
                    not marketplace_name or len(marketplace_name) > 1 or
                    (isinstance(marketplace, list) and marketplace_name[0] != row["marketplace-name"])
                )
            ):
                print("marketplace_name", marketplace_name)
                marketplace_name = row["marketplace-name"]
                marketplace = marketplace_env.search([
                    ("name", "=", marketplace_name)
                ])
                if not marketplace:
                    raise UserError("Please set a marketplace for this report!\n"
                                    "The system is not able to find the marketplace %s." % marketplace_name)
                self.write({"amz_marketplace_ids": [(6, 0, [marketplace.id])]})
                journal_marketplace = marketplace.journal_id

            if not journal_marketplace:
                raise UserError("Please set a journal for the marketplace %s" % marketplace_name)

            if row["transaction-type"] not in statement_lines_data:
                statement_lines_data[row["transaction-type"]] = {}
            data = statement_lines_data[row["transaction-type"]]
            label = ' | '.join([
                row["order-id"],
                row["transaction-type"],
                row["amount-type"],
                row["amount-description"]
            ])
            if row["merchant-order-id"]:
                label += (' | ' + row["merchant-order-id"])
            if row["adjustment-id"]:
                label += (' | ' + row["adjustment-id"])
            if row["sku"]:
                label += (' | ' + row["sku"])
            line_date = datetime.datetime.strptime(row['posted-date'], "%d.%m.%Y").date()
            line_amount = float(row["amount"].replace(",", "."))
            key = row["order-item-code"]
            if not key:
                key = row["order-id"]
            if not key:
                other_transactions_data.append({
                    "payment_ref": label,
                    "date": line_date,
                    "amount": line_amount,
                    "journal_id": journal_marketplace.id,
                })
            if key not in data:
                data[key] = {
                    "payment_ref": label,
                    "date": line_date,
                }
            vals = data[key]
            # if not vals:
                # vals["date"] = line_date
            if row["amount-type"] not in vals:
                vals[row["amount-type"]] = {}
            vals[row["amount-type"]].update({
                row["amount-description"]: line_amount
            })
            # statement_lines_data[row["transaction-type"]].update(vals)

        order_amount_data = []
        for _, vals in statement_lines_data.items():
            order_amount_data += (self.settlement_report_order_process(vals))

        stmt_lines = (other_transactions_data + order_amount_data)
        for sl in stmt_lines:
            sl.update({"journal_id": journal_marketplace.id})
        statement = self.env["account.bank.statement"].create({
            "name": '%s %s (%s => %s)' % (
                self.amz_marketplace_ids[0].name,
                statement_data["settlement-id"],
                statement_data["settlement-start-date"],
                statement_data["settlement-end-date"],
            ),
            "date": datetime.datetime.strptime(statement_data["deposit-date"][:10], "%d.%m.%Y").date(),
            "currency_id": self.env["res.currency"].search([('name', '=', statement_data["currency"])], limit=1).id,
            "journal_id": journal_marketplace.id,
            "line_ids": [(0, 0, line) for line in stmt_lines]
        })
        # self.env["account.bank.statement.line"].create(other_transactions_data + order_amount_data)
        self.write({
            "statement_id": statement.id,
            "state": "PROCESSED",
        })
        return True

    def settlement_report_order_process(self, order_amount_dict):
        sale_env = self.env["sale.order"]
        sale_line_env = self.env["sale.order.line"]
        res = []
        for line_id, value in order_amount_dict.items():
            if "-" in line_id:
                order = sale_env.search([
                    "|",
                    ('amazon_order_ref', '=', line_id),
                    ('name', '=', line_id),
                ])
                payment_ref = value.pop("payment_ref")
                date = value.pop("date")
                for i, j in value.items():
                    for k, l in j.items():
                        res.append({
                            "payment_ref": payment_ref,
                            "sale_order_id": order.id,
                            "partner_id": order.partner_id.id,
                            "date": date,
                            "amount": l,
                        })
                continue
            order_line = sale_line_env.search([('amazon_item_ref', '=', line_id)])
            order = order_line.order_id
            item_price = value.pop("ItemPrice", {})
            promotion = value.pop("Promotion", {})
            price_net_amount = float(item_price.pop("Principal", 0.0))
            price_tax_amount = float(item_price.pop("Tax", 0.0))
            discount_net_amount = float(promotion.pop("Principal", 0.0))
            discount_tax_amount = float(promotion.pop("TaxDiscount", 0.0))
            ship_net_amount = float(item_price.pop("Shipping", 0.0))
            ship_tax_amount = float(item_price.pop("ShippingTax", 0.0))
            vals = {
                "payment_ref": value["payment_ref"],  # " | ".join([order.amazon_order_ref, order_line.product_id.default_code or line_id]),
                "sale_line_id": order_line.id,
                "sale_order_id": order.id,
                "partner_id": order.partner_id.id,
                "date": value["date"],
                "amount": sum([
                    price_net_amount,
                    price_tax_amount,
                    discount_net_amount,
                    discount_tax_amount,
                    ship_net_amount,
                    ship_tax_amount,
                ]),
            }
            res.append(vals)
            for key, amount in item_price.items():
                res.append({
                    "payment_ref": " | ".join([order.amazon_order_ref or "", key]),
                    "sale_line_id": order_line.id,
                    "sale_order_id": order.id,
                    "partner_id": order.partner_id.id,
                    "date": value["date"],
                    "amount": float(amount),
                })
            for key, amount in promotion.items():
                res.append({
                    "payment_ref": " | ".join([order.amazon_order_ref or "", key]),
                    "sale_line_id": order_line.id,
                    "sale_order_id": order.id,
                    "partner_id": order.partner_id.id,
                    "date": value["date"],
                    "amount": float(amount),
                })

            item_fee = value.pop("ItemFees", {})
            for key, amount in item_fee.items():
                res.append({
                    "payment_ref": " | ".join([order.amazon_order_ref or "", key]),
                    "sale_line_id": order_line.id,
                    "sale_order_id": order.id,
                    "partner_id": order.partner_id.id,
                    "date": value["date"],
                    "amount": float(amount),
                })
        return res

    def button_view_statement_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Statements Lines",
            "res_model": "account.bank.statement.line",
            "view_mode": "tree,form",
            "domain": [("statement_id", "=", self.statement_id.id)],
        }
