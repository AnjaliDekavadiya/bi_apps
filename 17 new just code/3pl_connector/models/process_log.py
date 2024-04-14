# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProcessLog(models.Model):
    _name = "process.log"
    _description = "Process Log"
    _order = "id desc"

    name = fields.Char("Name", copy=False, help="Process Log Reference.")
    process_datetime = fields.Datetime("Process Datetime", copy=False, help="Date and Time when process started.")
    application = fields.Selection([("product", "Product"),
                                    ("sales", "Sales Transfer"),
                                    ("sales_return", "Sales Return Transfer"),
                                    ("purchase", "Purchase Transfer"),
                                    ("stock", "Stock")],
                                   "Application", required=True, copy=False, help="Application affected in file process.")
    operation = fields.Selection([("import", "Import"),
                                  ("export", "Export")],
                                 "Operation", required=True, copy=False, help="Operation performed during process.")
    file_name = fields.Char("File Name", copy=False, help="File Name which is processed.")
    company_id = fields.Many2one("res.company", required=True, copy=False, default=lambda self: self.env.company.id, help="Related Company.")
    note = fields.Text("Note", copy=False, help="Notes related to file process.")
    process_log_line_ids = fields.One2many("process.log.line", "process_log_id", "Process Log Lines", help="Process Log Lines for each file line details.")
    company_id = fields.Many2one("res.company", required=True, copy=False, default=lambda self: self.env.company.id,
                                 help="Related Company")


class ProcessLogLine(models.Model):
    _name = "process.log.line"
    _description = "Process Log Line"
    _rec_name = "picking_id"

    process_log_id = fields.Many2one("process.log", "Process Log", help="Related Process Log.")
    product_id = fields.Many2one("product.product", "Product", copy=False, help="Related Product.")
    picking_id = fields.Many2one("stock.picking", "Picking", copy=False, help="Related Picking.")
    exported_qty = fields.Float("Exported Qty", copy=False, help="No Of Quantity Exported from odoo to process.")
    file_qty = fields.Float("File Qty", copy=False, help="Actual processed quantity received in file.")
    difference_qty = fields.Float("Difference Qty", compute="get_difference_qty", store=True, help="Difference in Exported Quantity and File Quantity.")
    is_mismatch = fields.Boolean("Mismatch", copy=False, help="True, If this line has mismatch.")
    is_skip_line = fields.Boolean("Skip Line", copy=False, help="True, If line did not process due to some mismatch and skipped to next line.")
    is_skip_order = fields.Boolean("Skip Order", copy=False, help="True, If order did not processed due to some mismatched and skipped to next order.")
    message = fields.Text("Message", copy=False, help="Line Process Message.")
    company_id = fields.Many2one("res.company", required=True, copy=False, default=lambda self: self.env.company.id,
                                 help="Related Company")

    @api.depends("exported_qty", "file_qty")
    def get_difference_qty(self):
        for record in self:
            record.difference_qty = abs(record.exported_qty - record.file_qty)
