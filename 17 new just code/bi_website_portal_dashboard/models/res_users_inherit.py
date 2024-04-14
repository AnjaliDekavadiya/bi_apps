# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import datetime


class ResUsersInherit(models.Model):
	_inherit = 'res.users'

	filt = fields.Integer();

	def delete_grid_settings(self):
		objs= self.env['grid.data'].sudo().search([]);
		for obj in objs:
			obj.check = False;

	def set_grid_setting(self,data):
		obj = self.env['grid.data'];
		rec = obj.sudo().search([("url","=",data[1])]);
		if rec:
			rec.sudo().write({"name" : data[0],
							"url" : data[1],
							"icon" : data[2],
							"color" : data[3],
							"count" : data[4],
							"check" : True,});
		else:
			obj.sudo().create({"name" : data[0],
								"url" : data[1],
								"icon" : data[2],
								"color" : data[3],
								"count" : data[4],
								"placeholder_count" : data[5],
								"check" : True,});
		return 0;


	def grid_settings(self):
		# Inherit this method to set color and icon for newlly added grids 
		return {"/my/quotes" : ['fa fa-dollar', '#04becf'],
				"/my/orders" : ['fa fa-line-chart', '#e84dd3'],
				"/my/invoices?filterby=invoices" : ['fa fa-money', '#2cb049'],
				"/my/invoices?filterby=bills" : ['fa fa-money', '#2cb049'],
				"/my/timesheets" : ['fa fa-clock-o', '#a6269b'],
				"/my/projects" : ['fa fa-puzzle-piece', '#db452e'],
				"/my/tasks" : ['fa fa-tasks', '#8b5cc4'],
				"/my/purchase" : ['fa fa-shopping-cart', '#4248f5'],
				"/my/account" : ['fa fa-user', '#db8400'],
				"/my/tickets" : ['fa fa-ticket','#c2ed4a'],
				"/my/leads" : ['fa fa-handshake-o','#298c64'],
				"/my/security" : ['fa fa-expeditedssl','#495057'],
				"/my/opportunities" : ['fa fa-star','#96627b'],}


	def check_crm_module(self):
		if self.env["ir.ui.view"].sudo().search([("key",'=','website_crm_partner_assign.portal_my_home_lead')]):
			return True;
		else:
			return False;

	def check_table_first(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if not (setting['show_quotaion_table'] and setting['show_so_table']):
			return 'full_table_view';
		elif setting['show_quotaion_table'] and setting['show_so_table']:
			return 'half_table_view';


	def check_table_second(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if not (setting['show_po_table'] and setting['show_rfq_table']):
			return 'full_table_view';
		elif setting['show_po_table'] and setting['show_rfq_table']:
			return 'half_table_view';


	def check_table_third(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if not (setting['show_invoice_table'] and setting['show_bill_table']):
			return 'full_table_view';
		elif setting['show_invoice_table'] and setting['show_bill_table']:
			if not (self.partner_id.is_vendor and self.partner_id.is_customer):
				if (self.partner_id.is_vendor == False and self.partner_id.is_customer == False):
					return 'half_product_table_view';
				return 'full_table_view';
			return 'half_table_view';


	def check_chart_first(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if setting['show_sale_chart'] and setting['show_invoice_chart']:
			return 'half_chart_view';


	def check_chart_second(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if setting['show_purchase_chart'] and setting['show_bill_chart']:
			return 'half_chart_view';

	def check_chart_product(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if setting['show_purchase_chart'] and setting['show_sale_chart']:
			if not (self.partner_id.is_vendor and self.partner_id.is_customer):
				if (self.partner_id.is_vendor == False and self.partner_id.is_customer == False):
					return 'half_chart_product_view';

	def check_table_product(self):
		setting = self.env['res.config.settings'].sudo().get_values();
		if not (setting['show_purchase_chart'] and setting['show_sale_chart']):
			return 'full_product_table_view';
		elif setting['show_purchase_chart'] and setting['show_sale_chart']:
			if not (self.partner_id.is_vendor and self.partner_id.is_customer):
				if (self.partner_id.is_vendor == False and self.partner_id.is_customer == False):
					return 'half_product_table_view';
				return 'full_product_table_view';
			return 'half_product_table_view';



	def get_filtered_obj(self,objs,index,tag):
		i = index-1;
		if len(objs) == 0:
			return objs;
		date = [[datetime.date.today()],
				[datetime.date.today()-datetime.timedelta(days=1)],
				[datetime.date.today()-datetime.timedelta(days=datetime.date.today().weekday()),
					datetime.date.today()+datetime.timedelta(days=6-datetime.date.today().weekday())],
				[datetime.date.today()-datetime.timedelta(days=datetime.date.today().day-1),
					datetime.date.today()+relativedelta(day=31)],
				[datetime.date(datetime.date.today().year, 1, 1),
					datetime.date(datetime.date.today().year, 12, 31)],];

		if index in [1,2]:
			if tag == 'orders':
				obj = objs.filtered(lambda s: s.date_order.date() == date[i][0]);
			else:
				obj = objs.filtered(lambda s: s.invoice_date == date[i][0]);
		if index in [3,4,5]:
			if tag == 'orders':
				obj = objs.filtered(lambda s: date[i][0] <= s.date_order.date() <= date[i][1]);
			else:
				obj = objs.filtered(lambda s: date[i][0] <= s.invoice_date <= date[i][1]);
		return obj;


	def get_quotation(self,user_id):
		if 'sale.order' in self.env:
			quotes = self.env['sale.order'].sudo().search([("state","in",["draft","sent"]),("user_id","=",user_id.id)]);
			quotes = self.get_filtered_obj(quotes,self.filt,'orders');
			setting = self.env['res.config.settings'].sudo().get_values();
			if len(quotes) == 0:
				return False;
			else:
				return quotes[:setting['no_records']];
		else:
			return False;

	def get_orders_status(self,obj,flag):
		if flag == "so":
			if obj.state == "cancel":
				return 4;
			cnt_d = 0;
			cnt_t = 0;
			for order in obj.order_line:
				cnt_d += order.qty_delivered;
				cnt_t += order.product_uom_qty;
			if cnt_d == 0:
				return 1;
			if cnt_d < cnt_t:
				return 2;
			if cnt_d == cnt_d:
				return 3;
		elif flag =="po":
			if obj.state == "cancel":
				return 4;
			cnt_d = 0;
			cnt_t = 0;
			for order in obj.order_line:
				cnt_d += order.qty_received;
				cnt_t += order.product_qty;
			if cnt_d == 0:
				return 1;
			if cnt_d < cnt_t:
				return 2;
			if cnt_d == cnt_d:
				return 3;


	def get_sale_orders(self,user_id):
		if 'sale.order' in self.env:
			sale_orders = self.env['sale.order'].sudo().search([("state","in",["sale","cancel"]),("user_id","=",user_id.id)]);
			sale_orders = self.get_filtered_obj(sale_orders,self.filt,'orders');
			setting = self.env['res.config.settings'].sudo().get_values()
			if len(sale_orders) == 0:
				return False;
			else:
				return sale_orders[:setting['no_records']];
		else:
			return False;


	def get_rfqs(self,user_id):
		if 'purchase.order' in self.env:
			rfqs = self.env['purchase.order'].sudo().search([("state","=","draft"),("user_id","=",user_id.id)]);
			rfqs = self.get_filtered_obj(rfqs,self.filt,'orders');
			setting = self.env['res.config.settings'].sudo().get_values()
			if len(rfqs) == 0:
				return False;
			else:
				return rfqs[:setting['no_records']];
		else:
			return False;


	def get_purchase_orders(self,user_id):
		if 'purchase.order' in self.env:
			purchase_orders = self.env['purchase.order'].sudo().search([("state","in",["purchase","cancel"]),("user_id","=",user_id.id)]);
			purchase_orders = self.get_filtered_obj(purchase_orders,self.filt,'orders');
			setting = self.env['res.config.settings'].sudo().get_values()
			if len(purchase_orders) == 0:
				return False;
			else:
				return purchase_orders[:setting['no_records']];
		else:
			return False;


	def get_invoices(self,user_id):
		if 'account.move' in self.env:
			invoices = self.env['account.move'].sudo().search([("move_type","=","out_invoice"),("invoice_user_id","=",user_id.id)]);
			invoices = self.get_filtered_obj(invoices,self.filt,'invoices');
			setting = self.env['res.config.settings'].sudo().get_values()
			if len(invoices) == 0:
				return False;
			else:
				return invoices[:setting['no_records']];
		else:
			return False;


	def get_bills(self,user_id):
		if 'account.move' in self.env:
			bills = self.env['account.move'].sudo().search([("move_type","=","in_invoice"),("invoice_user_id","=",user_id.id)]);
			bills = self.get_filtered_obj(bills,self.filt,'invoices');
			setting = self.env['res.config.settings'].sudo().get_values();
			if len(bills) == 0:
				return False;
			else:
				return bills[:setting['no_records']];
		else:
			return False;



	def string_formatted(self,x):
		if x.find('(') == -1:
			return x[0:];
		else:
			return x[0:x.find('(')];



	def get_solds(self,user):
		if 'sale.order' in self.env:
			sos = self.env['sale.order'].sudo().search([("user_id",'=',user.id),('state','=','sale')]);
			sos = self.get_filtered_obj(sos,5,'orders');
			temp = {};
			if len(sos):
				for so in sos:
					for line in so.order_line:
						if line.product_id.id in temp.keys():
							temp[line.product_id.id][2] += float('%.2f'%(line.product_uom_qty * line.price_unit));
							temp[line.product_id.id][3] += line.product_uom_qty;
						else:
							temp[line.product_id.id] = [line.product_id, self.string_formatted(line.product_id.name), float('%.2f'%(line.product_uom_qty * line.price_unit)), line.product_uom_qty];
			temp = dict(sorted(temp.items(), key=lambda item: item[1][2] ,reverse=True));
			if len(temp.keys()) > 10:
				temp = dict(list(temp.items())[0:10]);
			return temp;
		else:
			return False;



	def get_purchases(self,user):
		if 'purchase.order' in self.env:
			pos = self.env['purchase.order'].sudo().search([("user_id",'=',user.id),('state','=','purchase')]);
			pos = self.get_filtered_obj(pos,5,'orders');
			temp = {};
			if len(pos):
				for po in pos:
					for line in po.order_line:
						if line.product_id.id in temp.keys():
							temp[line.product_id.id][2] += float('%.2f'%(line.product_uom_qty * line.price_unit));
							temp[line.product_id.id][3] += line.product_uom_qty;
						else:
							temp[line.product_id.id] = [line.product_id, self.string_formatted(line.product_id.name),float('%.2f'%(line.product_uom_qty * line.price_unit)), line.product_uom_qty];
			temp = dict(sorted(temp.items(), key=lambda item: item[1][2] ,reverse=True));
			if len(temp.keys()) > 10:
				temp = dict(list(temp.items())[0:10]);
			return temp;
		else:
			return False;


	def get_projects(self,user):
		if 'project.task' in self.env:
			tasks = self.env['project.task'].search([]);
			return tasks;
		else:
			return False;

