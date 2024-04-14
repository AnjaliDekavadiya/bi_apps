# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_3pl_warehouse = fields.Boolean("3PL Warehouse",
        default=False,
        copy=False,
        help="Check True, If this warehouse is 3PL warehouse.",)
    ftp_server_id = fields.Many2one("ftp.server", "FTP Server", ondelete="restrict", help="Related FTP Server.")
    import_ftp_files_to = fields.Char("Import FTP Files To",
        copy=False,
        help="Local directory of your server where you want to import file to process.",)  # Files will be deleted automatically after processing.
    export_product_to = fields.Many2one("ftp.directory",
        "Product Export To",
        copy=False,
        help="Export product file to this directory.",)
    is_auto_export_products = fields.Boolean("Automatically Export Products",
        copy=False,
        default=False,
        help="Export products automatically whenever cron is executed.",)
    export_product_prefix = fields.Char("Product Prefix", help="Prefix for export products file.")
    export_product_file_type = fields.Selection([("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "Product File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    last_export_product_datetime = fields.Datetime("Last Product Export At")
    is_notify_users_when_export_products = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process export products operation.",)
    export_product_email_template_id = fields.Many2one("mail.template",
        "Email Template",
        ondelete="restrict", 
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_export_products'),
        help="This template will be used to send email when process export products operation.",)
    notify_user_ids_export_products = fields.Many2many("res.users",
        "warehouse_users_product_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process export product operation.",)
    export_sales_to = fields.Many2one("ftp.directory",
        "Sales Export To",
        copy=False,
        help="Export sale file to this directory.",)
    is_auto_export_sales = fields.Boolean("Automatically Export Sales Transfers",
        copy=False,
        default=False,
        help="Export Sales automatically whenever cron is executed.",)
    export_sales_prefix = fields.Char("Sales Prefix", help="Prefix for export sales file.")
    export_sales_file_type = fields.Selection([("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    last_export_sale_datetime = fields.Datetime("Last Sales Export At")
    is_notify_users_when_export_sales = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process export sales operation.",)
    export_sales_email_template_id = fields.Many2one("mail.template",
        "Sales Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_export_sales'),
        help="This template will be used to send email when process export sales operation.",)  
    notify_user_ids_export_sales = fields.Many2many("res.users",
        "warehouse_users_sales_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process export sales operation.",)
    import_sales_res_from = fields.Many2one("ftp.directory",
        "Import From",
        copy=False,
        help="Import sale response file from this directory.",)
    is_auto_import_sales_res = fields.Boolean("Automatically Import Sales Transfers Response",
        copy=False,
        default=False,
        help="Import sales response automatically whenever cron is executed.",)
    import_sales_res_prefix = fields.Char("Sales Prefix", help="Prefix for import sales response file.")
    import_sales_res_file_type = fields.Selection([("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    move_processed_sale_file_to = fields.Many2one("ftp.directory",
        "Move Processed File To",
        copy=False,
        help="Move Processed Files To This Folder So In Next Import Only New Files Will Be There.",)
    is_notify_users_when_import_sales = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process import sales operation.",)
    import_sales_email_template_id = fields.Many2one("mail.template",
        "Sales Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_import_sales'),
        help="This template will be used to send email when process import sales operation.",) 
    notify_user_ids_import_sales = fields.Many2many("res.users",
        "warehouse_users_sales_res_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process import sales operation.",)

    export_sale_return_to = fields.Many2one("ftp.directory",
        "Sale Return Export To",
        copy=False,
        help="Export sale return file to this directory.",)
    is_auto_export_sales_return = fields.Boolean("Automatically Export Sales Return Transfers",
        copy=False,
        default=False,
        help="Export Sales return automatically whenever cron is executed.",)
    export_sale_return_prefix = fields.Char("Prefix", help="Prefix for export sales return file.")
    export_sales_return_file_type = fields.Selection([("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    last_export_sale_return_datetime = fields.Datetime("Last Sales Return Export At")
    is_notify_users_when_export_sales_return = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process export sales return operation.",)
    export_sales_return_email_template_id = fields.Many2one("mail.template",
        "Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_export_sales_return'),
        help="This template will be used to send email when process export sales return operation.",)  
    notify_user_ids_export_sales_return = fields.Many2many("res.users",
        "warehouse_users_sales_return_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process export sales return operation.",)

    import_sale_return_res_from = fields.Many2one("ftp.directory",
        "Import From",
        copy=False,
        help="Import sale return file to this directory.",)
    is_auto_import_sales_return = fields.Boolean("Automatically Import Sales Return Transfers Response",
        copy=False,
        default=False,
        help="Import Sales return response automatically whenever cron is executed.",)
    import_sale_return_res_prefix = fields.Char(
        "Prefix", help="Prefix for export sales return response file.")
    import_sales_return_res_file_type = fields.Selection(
        [("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    move_processed_sale_return_file_to = fields.Many2one("ftp.directory",
        "Move Processed File To",
        copy=False,
        help="Move Processed Files To This Folder So In Next Import Only New Files Will Be There.",)
    is_notify_users_when_import_sales_return = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process import sales return operation.",)
    import_sales_return_email_template_id = fields.Many2one("mail.template",
        "Sale Return Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_import_sales_return'),
        help="This template will be used to send email when process import sales return operation.",)  
    notify_user_ids_import_sales_return = fields.Many2many("res.users",
        "warehouse_users_sales_return_res_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process import sales return operation.",)
    export_purchase_to = fields.Many2one("ftp.directory",
        "Export To",
        copy=False,
        help="Export purchase file to this directory.",)
    is_auto_export_purchase = fields.Boolean("Automatically Export Purchase Transfers",
        copy=False,
        default=False,
        help="Export purchase automatically whenever cron is executed.",)
    export_purchase_prefix = fields.Char("Prefix", help="Prefix for export purchase file.")
    export_purchase_file_type = fields.Selection(
        [("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    last_export_purchase_datetime = fields.Datetime("Last Purchase Export At")
    is_notify_users_when_export_purchase = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process export purchase operation.",)
    export_purchase_email_template_id = fields.Many2one("mail.template",
        "Purchase Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_export_purchase'),
        help="This template will be used to send email when process export purchase operation.",) 
    notify_user_ids_export_purchase = fields.Many2many("res.users",
        "warehouse_users_purchase_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process export purchase operation.",)

    import_purchase_res_from = fields.Many2one("ftp.directory",
        "Import From",
        copy=False,
        help="Import purchase res file from this directory.",)
    is_auto_import_purchase_res = fields.Boolean("Automatically Import Purchase Transfers Response",
        copy=False,
        default=False,
        help="Import purchase response automatically whenever cron is executed.",)
    import_purchase_res_prefix = fields.Char("Prefix", help="Prefix for import purchase res file.")
    import_purchase_res_file_type = fields.Selection(
        [("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    move_processed_purchase_file_to = fields.Many2one("ftp.directory",
        "Move Processed File To",
        copy=False,
        help="Move Processed Files To This Folder So In Next Import Only New Files Will Be There.",)
    is_notify_users_when_import_purchase = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process import purchase operation.",)
    import_purchase_email_template_id = fields.Many2one("mail.template",
        "Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_import_purchase'),
        help="This template will be used to send email when process import purchase operation.",)  
    notify_user_ids_import_purchase = fields.Many2many("res.users",
        "warehouse_users_purchase_res_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process import purchase operation.",)
    import_stock_file_from = fields.Many2one("ftp.directory",
        "Import From",
        copy=False,
        help="Import stock file from this directory.",)
    is_auto_import_stock = fields.Boolean("Automatically Import Stock",
        copy=False,
        default=False,
        help="Import stock automatically whenever cron is executed.",)
    import_stock_res_prefix = fields.Char("Prefix", help="Prefix for export stock file.")
    import_stock_file_type = fields.Selection(
        [("excel", "Excel(xlsx)"), ("csv", "CSV")],
        "File Type",
        default="excel",
        required=True,
        help="File Type to be used in 3PL connection and data exchange.",)
    move_processed_stock_file_to = fields.Many2one("ftp.directory",
        "Move Processed File To",
        copy=False,
        help="Move Processed Files To This Folder So In Next Import Only New Files Will Be There.",)
    is_notify_users_when_import_stock = fields.Boolean("Notify Users?",
        default=False,
        copy=False,
        help="Notify users when process import stock operation.",)
    import_stock_email_template_id = fields.Many2one("mail.template",
        "Email Template",
        ondelete="restrict",
        default=lambda self: self.env['ir.model.data']._xmlid_to_res_id('3pl_connector.email_template_import_stock'),
        help="This template will be used to send email when process import stock operation.",)  
    notify_user_ids_import_stock = fields.Many2many("res.users",
        "warehouse_users_stock_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process import stock operation.")
     
    notify_user_ids_import_sales_return = fields.Many2many("res.users",
        "warehouse_users_purchase_return_res_rel",
        "warehouse_id",
        "user_id",
        "Users To Notify",
        help="Users to whom mail will be sent when process import Sales return operation.",)

    is_product_process = fields.Boolean("Product Export Process", related="ftp_server_id.is_product_process")
    is_sales_process = fields.Boolean("Sales Transfer Process", related="ftp_server_id.is_sales_process")
    is_sales_return_process = fields.Boolean("Sales Return Transfer Process", related="ftp_server_id.is_sales_return_process")
    is_purchase_process = fields.Boolean("Sales Purchase Process", related="ftp_server_id.is_purchase_process")
    is_stock_process = fields.Boolean("Stock Import Process", related="ftp_server_id.is_stock_process")
    is_auto_validate_inventory = fields.Boolean('Auto Validate Inventory', default=True)

    @api.onchange('ftp_server_id')
    def onchange_ftp_server_id(self):
      for rec in self:
            rec.import_ftp_files_to = ''
            rec.export_product_to = False
            rec.export_sales_to = False
            rec.import_sales_res_from = False
            rec.export_sale_return_to = False
            rec.import_sale_return_res_from = False
            rec.export_purchase_to = False
            rec.import_purchase_res_from = False
            rec.import_stock_file_from = False

            rec.is_auto_export_products = False
            rec.is_auto_export_sales = False
            rec.is_auto_import_sales_res = False
            rec.is_auto_export_sales_return = False
            rec.is_auto_import_sales_return = False
            rec.is_auto_export_purchase = False
            rec.is_auto_import_purchase_res = False
            rec.is_auto_import_stock = False

    @api.onchange('is_notify_users_when_export_products')
    def onchange_is_notify_users_when_export_products(self):
      template_id = self.env.ref('3pl_connector.email_template_export_products')
      for rec in self:
        if template_id and rec.is_notify_users_when_export_products:
          rec.export_product_email_template_id = template_id.id
        else:
          rec.export_product_email_template_id = False

    @api.onchange('is_notify_users_when_export_sales')
    def onchange_is_notify_users_when_export_sales(self):
      template_id = self.env.ref('3pl_connector.email_template_export_sales')
      for rec in self:
        if template_id and rec.is_notify_users_when_export_sales:
          rec.export_sales_email_template_id = template_id.id
        else:
          rec.export_sales_email_template_id = False

    @api.onchange('is_notify_users_when_import_sales')
    def onchange_is_notify_users_when_import_sales(self):
      template_id = self.env.ref('3pl_connector.email_template_import_sales')
      for rec in self:
        if template_id and rec.is_notify_users_when_import_sales:
          rec.import_sales_email_template_id = template_id.id
        else:
          rec.import_sales_email_template_id = False

    @api.onchange('is_notify_users_when_export_sales_return')
    def onchange_is_notify_users_when_export_sales_return(self):
      template_id = self.env.ref('3pl_connector.email_template_export_sales_return')
      for rec in self:
        if template_id and rec.is_notify_users_when_export_sales_return:
          rec.export_sales_return_email_template_id = template_id.id
        else:
          rec.export_sales_return_email_template_id = False

    @api.onchange('is_notify_users_when_import_sales_return')
    def onchange_is_notify_users_when_import_sales_return(self):
      template_id = self.env.ref('3pl_connector.email_template_import_sales_return')
      for rec in self:
        if template_id and rec.is_notify_users_when_import_sales_return:
          rec.import_sales_return_email_template_id = template_id.id
        else:
          rec.import_sales_return_email_template_id = False

    @api.onchange('is_notify_users_when_export_purchase')
    def onchange_is_notify_users_when_export_purchase(self):
      template_id = self.env.ref('3pl_connector.email_template_export_purchase')
      for rec in self:
        if template_id and rec.is_notify_users_when_export_purchase:
          rec.export_purchase_email_template_id = template_id.id
        else:
          rec.export_purchase_email_template_id = False

    @api.onchange('is_notify_users_when_import_purchase')
    def onchange_is_notify_users_when_import_purchase(self):
      template_id = self.env.ref('3pl_connector.email_template_import_purchase')
      for rec in self:
        if template_id and rec.is_notify_users_when_import_purchase:
          rec.import_purchase_email_template_id = template_id.id
        else:
          rec.import_purchase_email_template_id = False

    @api.onchange('is_notify_users_when_import_stock')
    def onchange_is_notify_users_when_import_stock(self):
      template_id = self.env.ref('3pl_connector.email_template_import_stock')
      for rec in self:
        if template_id and rec.is_notify_users_when_import_stock:
          rec.import_stock_email_template_id = template_id.id
        else:
          rec.import_stock_email_template_id = False
