# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re


class TplOperations(models.TransientModel):
    _name = "tpl.operations"
    _description = "Tpl Operations"

    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1).id

    warehouse_id = fields.Many2one("stock.warehouse", required=True,
        domain=[("is_3pl_warehouse", "=", True)],
        default=_default_warehouse_id,
        help="Related Warehouse to process operations.")
    import_sales = fields.Boolean("Sales Transfer", default=False,
        help="Import Sales File.")
    import_sales_return = fields.Boolean("Sales Return Transfer", default=False, 
        help="Import Sales Return File.")
    import_purchase = fields.Boolean("Purchase Transfer", default=False, 
        help="Import Purchase File.")
    import_stock = fields.Boolean("Stock", default=False, help="Import Stock File.")
    export_product = fields.Boolean("Product", default=False, 
        help="Export Product File.")
    export_sales = fields.Boolean("Sales Transfer", default=False, 
        help="Export Sales File.")
    export_sales_return = fields.Boolean("Sales Return Transfer", 
        default=False, help="Export Sales Return File.")
    export_purchase = fields.Boolean("Purchase Transfer", default=False, 
        help="Export Sales File.")
    export_product_ids = fields.Many2many("product.product", 
        "product_export_3pl_rel", "operation_id", "product_id",
        "Products", domain="[('type', '=', 'product')]",
        help="These product data will be exported to 3PL.")
    export_so_picking_ids = fields.Many2many("stock.picking", 
        "picking_export_3pl_rel", "operation_id", "picking_id",
        "Sales Pickings", 
        domain="[('picking_type_code', '=', 'outgoing'), ('state', 'not in', ['done', 'cancel'])]", 
        help="These pickings data will be exported to 3PL.")
    export_sr_picking_ids = fields.Many2many("stock.picking", 
        "picking_sr_export_3pl_rel", "operation_id", "picking_id",
        "Sales Return Pickings", 
        domain="[('picking_type_code', '=', 'incoming'), ('move_ids.origin_returned_move_id', '!=', False), ('state', 'not in', ['done', 'cancel'])]",
        help="These pickings data will be exported to 3PL.")
    export_po_picking_ids = fields.Many2many("stock.picking", 
        "picking_po_export_3pl_rel", "operation_id", "picking_id", 
        "Purchase Pickings", 
        domain="[('picking_type_code', '=', 'incoming'), ('move_ids.origin_returned_move_id', '=', False), ('state', 'not in', ['done', 'cancel'])]",
        help="These pickings data will be exported to 3PL.")
    stock_location = fields.Char("Location", 
        help="Stock will be updated in this location.")
    operation = fields.Selection([('import', 'Import'), ('export', 'Export')], required=True, default='import')
    is_export_product = fields.Boolean(default=False)
    is_stock = fields.Boolean(default=False)
    is_sales_transfer = fields.Boolean(default=False)
    is_sales_return_transfer = fields.Boolean(default=False)
    is_purchase_transfer = fields.Boolean(default=False)

    @api.onchange("warehouse_id")
    def _compute_product_boolean_fields(self):
        stock_warehouse_obj = self.env["stock.warehouse"].search([('id', '=', self.warehouse_id.id)])
        if stock_warehouse_obj.ftp_server_id.is_product_process == False:
            self.is_export_product = True
        if stock_warehouse_obj.ftp_server_id.is_stock_process == False:
            self.is_stock = True
        if stock_warehouse_obj.ftp_server_id.is_sales_process == False:
            self.is_sales_transfer = True
        if stock_warehouse_obj.ftp_server_id.is_sales_return_process == False:
            self.is_sales_return_transfer = True
        if stock_warehouse_obj.ftp_server_id.is_purchase_process == False:
            self.is_purchase_transfer = True

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.export_product:
            self.onchange_export_product()
        if self.export_sales:
            self.onchange_export_sales()
        if self.export_sales_return:
            self.onchange_export_sales_return()
        if self.export_purchase:
            self.onchange_export_purchase()
        if self.import_stock and self.warehouse_id:
            self.stock_location = "Stock will be updated in '%s' location." % self.warehouse_id.lot_stock_id.display_name

    @api.onchange("export_purchase")
    def onchange_export_purchase(self):
        stock_move_obj = self.env["stock.move"]
        picking_type_id = self.env["stock.picking.type"].sudo().search([('warehouse_id', '=', self.warehouse_id.id)])
        self.export_sr_picking_ids = [(6, 0, [])]
        if self.export_purchase:
            move_domain = [("picking_id.picking_type_code", "=", "incoming"),
                           ("origin_returned_move_id", "=", False),
                           ("picking_id.is_exported", "=", False),
                           ("state", "not in", ['done', 'cancel'])]

            if self.warehouse_id:
                move_domain += [
                    '|', '&',
                    ("company_id", "=", False),
                    ("company_id", "=", self.warehouse_id.company_id.id),
                    ('picking_type_id', 'in', picking_type_id.ids)
                ]
            if self.warehouse_id.last_export_purchase_datetime:
                move_domain.append(("create_date", ">", self.warehouse_id.last_export_purchase_datetime))
            moves = stock_move_obj.search(move_domain)
            pickings_to_export = moves.mapped("picking_id")
            self.export_po_picking_ids = [(6, 0, pickings_to_export.ids)]

    @api.onchange("import_stock")
    def onchange_import_stock(self):
        if self.import_stock and self.warehouse_id:
            self.stock_location = "Stock will be updated in '%s' location." % self.warehouse_id.lot_stock_id.display_name

    @api.onchange("export_sales_return")
    def onchange_export_sales_return(self):
        stock_move_obj = self.env["stock.move"]
        picking_type_id = self.env["stock.picking.type"].sudo().search([('warehouse_id', '=', self.warehouse_id.id)])
        self.export_sr_picking_ids = [(6, 0, [])]
        if self.export_sales_return:
            move_domain = [("picking_id.picking_type_code", "=", "incoming"),
                           ("origin_returned_move_id", "!=", False),
                           ("picking_id.is_exported", "=", False),
                           ("state", "not in", ['done', 'cancel'])]

            if self.warehouse_id:
                move_domain += [
                    '|', '&',
                    ("company_id", "=", False),
                    ("company_id", "=", self.warehouse_id.company_id.id),
                    ('picking_type_id', 'in', picking_type_id.ids)
                ]
            if self.warehouse_id.last_export_sale_return_datetime:
                move_domain.append(("create_date", ">", self.warehouse_id.last_export_sale_return_datetime))
            moves = stock_move_obj.search(move_domain)
            pickings_to_export = moves.mapped("picking_id")
            self.export_sr_picking_ids = [(6, 0, pickings_to_export.ids)]

    @api.onchange("export_sales")
    def onchange_export_sales(self):
        picking_obj = self.env["stock.picking"]
        picking_type_id = self.env["stock.picking.type"].sudo().search([('warehouse_id', '=', self.warehouse_id.id)])
        self.export_product_ids = [(6, 0, [])]
        if self.export_sales:
            picking_domain = [("picking_type_code", "=", "outgoing"),
                              ("is_exported", "=", False),
                              ("state", "not in", ['done', 'cancel'])]

            if self.warehouse_id:
                picking_domain += [
                    '|', '&',
                    ("company_id", "=", False),
                    ("company_id", "=", self.warehouse_id.company_id.id),
                    ('picking_type_id', 'in', picking_type_id.ids)
                ]
            if self.warehouse_id.last_export_sale_datetime:
                picking_domain.append(("create_date", ">", self.warehouse_id.last_export_sale_datetime))
            pickings_to_export = picking_obj.search(picking_domain)
            self.export_so_picking_ids = [(6, 0, pickings_to_export.ids)]

    @api.onchange("export_product")
    def onchange_export_product(self):
        product_obj = self.env["product.product"]
        self.sudo().export_product_ids = [(6, 0, [])]
        if self.export_product:
            product_domain = [("type", "=", "product")]
            if self.warehouse_id:
                product_domain += [
                    '|',
                    ("company_id", "=", False),
                    ("company_id", "=", self.warehouse_id.company_id.id)
                ]
            if self.warehouse_id and self.warehouse_id.last_export_product_datetime:
                product_domain.append(("create_date", ">", self.warehouse_id.last_export_product_datetime))
            products_to_export = product_obj.search(product_domain)
            self.sudo().export_product_ids = [(6, 0, products_to_export.ids)]

    def execute_processes(self):
        message = []
        if not self.warehouse_id.ftp_server_id or self.warehouse_id.ftp_server_id.state != 'confirmed':
            raise Warning(_("You have to confirm an instance to execute the process."))
        else:
            if self.export_product_ids and self.export_product:
                message.append(f"Export Product to this path {self.warehouse_id.export_product_to.path}")
                self.export_product_to_3pl()
            if self.export_sales:
                message.append( f"Export Sales to this path {self.warehouse_id.export_sales_to.path}")
                self.export_so_pickings_to_3pl()
            if self.export_sales_return:
                message.append(f"Export Sales Return to this path {self.warehouse_id.export_sale_return_to.path}")
                self.export_sr_pickings_to_3pl()
            if self.export_purchase:
                message.append(f"Export Purchase to this path {self.warehouse_id.export_purchase_to.path}")
                self.export_po_pickings_to_3pl()
            if self.import_stock:
                message.append(f"Import Stock form this path {self.warehouse_id.import_stock_file_from.path}")
                self.import_stock_from_3pl()
            if self.import_sales:
                message.append(f"Import Sales form this path {self.warehouse_id.import_sales_res_from.path}")
                self.import_so_response_from_3pl()
            if self.import_sales_return:
                message.append(f"Import Sales Return form this path {self.warehouse_id.import_sale_return_res_from.path}")
                self.import_sr_response_from_3pl()
            if self.import_purchase:
                message.append(f"Import Purchase form this path {self.warehouse_id.import_purchase_res_from.path}")
                self.import_po_response_from_3pl()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def export_product_to_3pl(self):
        if self.export_product_ids:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "product",
                "operation": "export",
                "company_id": self.warehouse_id.company_id.id
            }
            process_log = self.env["process.log"].create(vals)
            return self.export_product_ids.export_products_to_3pl(self.warehouse_id, process_log)
        else:
            raise UserError("You must select at least 1 product to export.")

    def export_so_pickings_to_3pl(self):
        if self.export_so_picking_ids:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "sales",
                "operation": "export",
                "company_id": self.warehouse_id.company_id.id
            }
            process_log = self.env["process.log"].create(vals)
            return self.export_so_picking_ids.export_so_pickings_to_3pl(self.warehouse_id, process_log)
        else:
            raise UserError("You must select at least 1 picking to export.")

    def export_sr_pickings_to_3pl(self):
        if self.export_sr_picking_ids:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "sales_return",
                "operation": "export",
                "company_id": self.warehouse_id.company_id.id
            }
            process_log = self.env["process.log"].create(vals)
            return self.export_sr_picking_ids.export_sr_pickings_to_3pl(self.warehouse_id, process_log)
        else:
            raise UserError("You must select at least 1 picking to export.")

    def export_po_pickings_to_3pl(self):
        if self.export_po_picking_ids:
            vals = {
                "name": self.env['ir.sequence'].next_by_code('3pl.process.log') or '/',
                "process_datetime": fields.datetime.now(),
                "application": "purchase",
                "operation": "export",
                "company_id": self.warehouse_id.company_id.id
            }
            process_log = self.env["process.log"].create(vals)
            return self.export_po_picking_ids.export_po_pickings_to_3pl(self.warehouse_id, process_log)
        else:
            raise UserError("You must select at least 1 picking to export.")

    def import_stock_from_3pl(self):
        return self.env["stock.quant"].import_stock_from_3pl(self.warehouse_id)

    def import_so_response_from_3pl(self):
        return self.env["stock.picking"].import_so_response_from_3pl(self.warehouse_id)

    def import_sr_response_from_3pl(self):
        return self.env["stock.picking"].import_sr_response_from_3pl(self.warehouse_id)

    def import_po_response_from_3pl(self):
        return self.env["stock.picking"].import_po_response_from_3pl(self.warehouse_id)
