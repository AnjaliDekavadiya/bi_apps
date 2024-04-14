# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettingsInherit(models.TransientModel):
	_inherit = 'res.config.settings'

	no_records = fields.Integer(string="No. of Latest Records You Want To Show",default=5);
	show_sale_chart = fields.Boolean(string= "Show Sales Analysis Chart");
	show_invoice_chart = fields.Boolean(string= "Show Invoice Analysis Chart");
	show_purchase_chart = fields.Boolean(string= "Show Purchase Analysis Chart");
	show_bill_chart = fields.Boolean(string= "Show Bill Analysis Chart");
	show_project_table = fields.Boolean(string= "Show Tasks and Projects Table");
	
	show_quotaion_table = fields.Boolean(string= "Show Latest Quotations");
	show_so_table = fields.Boolean(string= "Show Latest Sale Orders");
	show_rfq_table = fields.Boolean(string= "Show Latest RFQs");
	show_po_table = fields.Boolean(string= "Show Latest Purchase Orders");
	show_invoice_table = fields.Boolean(string= "Show Latest Invoices");
	show_bill_table = fields.Boolean(string= "Show Latest Bills");

	def set_values(self):
		res = super(ResConfigSettingsInherit, self).set_values();
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.no_records', self.no_records);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_sale_chart', self.show_sale_chart);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_invoice_chart', self.show_invoice_chart);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_purchase_chart', self.show_purchase_chart);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_bill_chart', self.show_bill_chart);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_project_table', self.show_project_table);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_quotaion_table', self.show_quotaion_table);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_so_table', self.show_so_table);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_rfq_table', self.show_rfq_table);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_po_table', self.show_po_table);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_invoice_table', self.show_invoice_table);
		self.env['ir.config_parameter'].sudo().set_param('bi_website_portal_dashboard.show_bill_table', self.show_bill_table);
		return res;

	def get_values(self):
		res = super(ResConfigSettingsInherit, self).get_values();
		res.update(
			no_records = int(self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.no_records')),
			show_sale_chart = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_sale_chart'),
			show_invoice_chart = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_invoice_chart'),
			show_purchase_chart = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_purchase_chart'),
			show_bill_chart = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_bill_chart'),
			show_project_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_project_table'),
			show_quotaion_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_quotaion_table'),
			show_so_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_so_table'),
			show_rfq_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_rfq_table'),
			show_po_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_po_table'),
			show_invoice_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_invoice_table'),
			show_bill_table = self.env['ir.config_parameter'].sudo().get_param('bi_website_portal_dashboard.show_bill_table'),);
		return res;