# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from dateutil.relativedelta import relativedelta
import datetime
import math


class WebsitePortalDashboard(http.Controller):

	@http.route(['/_get_chart_data'],type="json", auth="public", website=True)
	def _get_chart_data(self,index, **kw):
		index = int(index);
		i = index-1;
		user = request.env.user.id;
		data = [];
		date = [[datetime.date.today()],
				[datetime.date.today()-datetime.timedelta(days=1)],
				[datetime.date.today()-datetime.timedelta(days=datetime.date.today().weekday()),
					datetime.date.today()+datetime.timedelta(days=6-datetime.date.today().weekday())],
				[datetime.date.today()-datetime.timedelta(days=datetime.date.today().day-1),
					datetime.date.today()+relativedelta(day=31)],
				[datetime.date(datetime.date.today().year, 1, 1),
					datetime.date(datetime.date.today().year, 12, 31)],]
		if 'sale.order' in request.env:				
			so = request.env["sale.order"].sudo().search([('state','=','sale'),("user_id",'=',user)]);
		else:
			so = False;
		if 'purchase.order' in request.env:
			po = request.env["purchase.order"].sudo().search([('state','=','purchase'),("user_id",'=',user)]);
		else:
			po = False;
		if 'account.move' in request.env:
			inv = request.env["account.move"].sudo().search([("move_type","=","out_invoice"),('payment_state','=','paid'),("invoice_user_id",'=',user)]);
		else:
			inv = False;
		if 'account.move' in request.env:
			bill = request.env["account.move"].sudo().search([("move_type","=","in_invoice"),('payment_state','=','paid'),("invoice_user_id",'=',user)]);
		else:
			bill = False;

		if index==1:
			if so != False:
				so = so.filtered(lambda s: date[i][0]==s.date_order.date());
				total = sum([s.amount_total for s in so]);
			else:
				total = 0;
			data.append({'data':{"Today" : total,}, 'max' : self.roundup(total) if total else 400,});
			if po != False:
				po = po.filtered(lambda s: date[i][0]==s.date_order.date());
				total = sum([s.amount_total for s in po]);
			else:
				total = 0;
			data.append({'data':{"Today" : total,}, 'max' : self.roundup(total) if total else 400,});
			if inv != False:
				inv = inv.filtered(lambda s: date[i][0]==s.invoice_date);
				total = sum([s.amount_total_signed for s in inv]);
			else:
				total = 0;
			data.append({'data':{"Today" : total,}, 'max' : self.roundup(total) if total else 400,});
			if bill != False:
				bill = bill.filtered(lambda s: date[i][0]==s.invoice_date);
				total = sum([s.amount_total_signed for s in bill]);
			else:	
				total = 0;
			data.append({'data':{"Today" : total,}, 'max' : self.roundup(total) if total else 400,});
		
		elif index==2:
			if so != False:
				so = so.filtered(lambda s: date[i][0]==s.date_order.date());
				total = sum([s.amount_total for s in so]);
			else:
				total = 0;
			data.append({"data" : {"Yesterday" : total,}, 'max' : self.roundup(total) if total else 400,});
			if po != False:
				po = po.filtered(lambda s: date[i][0]==s.date_order.date());
				total = sum([s.amount_total for s in po]);
			else:
				total = 0;
			data.append({"data" : {"Yesterday" : total,}, 'max' : self.roundup(total) if total else 400,});			
			if inv != False:
				inv = inv.filtered(lambda s: date[i][0]==s.invoice_date);
				total = sum([s.amount_total_signed for s in inv]);
			else:
				total = 0;
			data.append({"data" : {"Yesterday" : total,}, 'max' : self.roundup(total) if total else 400,});
			if bill != False:
				bill = bill.filtered(lambda s: date[i][0]==s.invoice_date);
				total = sum([s.amount_total_signed for s in bill]);
			else:
				total = 0;
			data.append({"data" : {"Yesterday" : total,}, 'max' : self.roundup(total) if total else 400,});
		
		elif index==3:
			if so != False:
				so = so.filtered(lambda s: date[i][0]<=s.date_order.date()<=date[i][1]);
				data.append(self.get_week_data(so,'so'));
			else:
				data.append({'data' : {}, 'max' : 400,});
			if po != False:
				po = po.filtered(lambda s: date[i][0]<=s.date_order.date()<=date[i][1]);
				data.append(self.get_week_data(po,'po'));	
			else:
				data.append({'data' : {}, 'max' : 400,});	
			if inv != False:
				inv = inv.filtered(lambda s: date[i][0]<=s.invoice_date<=date[i][1]);
				data.append(self.get_week_data(inv,'inv'));
			else:
				data.append({'data' : {}, 'max' : 400,});
			if bill != False:
				bill = bill.filtered(lambda s: date[i][0]<=s.invoice_date<=date[i][1]);
				data.append(self.get_week_data(bill,'inv'));
			else:
				data.append({'data' : {}, 'max' : 400,});

		elif index==4:
			if so != False:
				so = so.filtered(lambda s: date[i][0]<=s.date_order.date()<=date[i][1]);
				data.append(self.get_month_data(so,'so'));
			else:
				data.append({'data' : {}, 'max' : 400,});
			if po != False:
				po = po.filtered(lambda s: date[i][0]<=s.date_order.date()<=date[i][1]);
				data.append(self.get_month_data(po,'po'));	
			else:
				data.append({'data' : {}, 'max' : 400,});
			if inv != False:
				inv = inv.filtered(lambda s: date[i][0]<=s.invoice_date<=date[i][1]);
				data.append(self.get_month_data(inv,'inv'));
			else:
				data.append({'data' : {}, 'max' : 400,});
			if bill != False:
				bill = bill.filtered(lambda s: date[i][0]<=s.invoice_date<=date[i][1]);
				data.append(self.get_month_data(bill,'inv'));
			else:
				data.append({'data' : {}, 'max' : 400,});

		elif index==5:
			if so != False:
				so = so.filtered(lambda s: date[i][0]<=s.date_order.date()<=date[i][1]);
				data.append(self.get_year_data(so,'so'));
			else:
				data.append({'data' : {}, 'max' : 400,});
			if po != False:
				po = po.filtered(lambda s: date[i][0]<=s.date_order.date()<=date[i][1]);
				data.append(self.get_year_data(po,'po'));	
			else:
				data.append({'data' : {}, 'max' : 400,});
			if inv != False:
				inv = inv.filtered(lambda s: date[i][0]<=s.invoice_date<=date[i][1]);
				data.append(self.get_year_data(inv,'inv'));
			else:
				data.append({'data' : {}, 'max' : 400,});
			if bill != False:
				bill = bill.filtered(lambda s: date[i][0]<=s.invoice_date<=date[i][1]);
				data.append(self.get_year_data(bill,'inv'));
			else:
				data.append({'data' : {}, 'max' : 400,});
		return data;



	def get_week_data(self,objs,tag):
		names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
		data = {};
		maximum=0
		for i in range(7):
			first_day = datetime.date.today()-datetime.timedelta(days=datetime.date.today().weekday()-i);
			if tag == "inv":
				obj = objs.filtered(lambda s: first_day == s.invoice_date);
				total = sum([s.amount_total for s in obj]);
			else:
				obj = objs.filtered(lambda s:first_day == s.date_order.date());
				total = sum([s.amount_total for s in obj]);	
			data[names[first_day.weekday()]] = total;
			if maximum < total:
				maximum = total;
		maximum = self.roundup(maximum) if maximum else 400;
		return {'data' : data, 
			'max' : maximum,};


	def get_month_data(self,objs,tag):
		names = ["Week 1","Week 2","Week 3","Week 4","Week 5"];
		data = {};
		maximum=0
		first_day = datetime.date.today()-datetime.timedelta(days=datetime.date.today().day-1);
		for i in range(5):
			last_day = first_day+datetime.timedelta(days=6);
			if last_day > datetime.date.today()+relativedelta(day=31):
				last_day = datetime.date.today()+relativedelta(day=31);
			if tag == "inv":
				obj = objs.filtered(lambda s:first_day <= s.invoice_date <= last_day);
				total = sum([s.amount_total for s in obj]);
			else:
				obj = objs.filtered(lambda s:first_day <= s.date_order.date() <= last_day);
				total = sum([s.amount_total for s in obj]);
			data[names[i]] = total;
			if maximum < total:
				maximum = total;
			first_day = last_day+datetime.timedelta(days=1);			
		maximum = self.roundup(maximum) if maximum else 400;
		return {'data' : data, 
			'max' : maximum};


	def get_year_data(self,objs,tag):
		names = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
		data = {};
		maximum=0
		first_day = datetime.date(datetime.date.today().year, 1, 1);
		for i in range(12):
			last_day = first_day+relativedelta(day=31);
			if tag == "inv":
				obj = objs.filtered(lambda s:first_day <= s.invoice_date <= last_day);
				total = sum([s.amount_total for s in obj]);
			else:
				obj = objs.filtered(lambda s:first_day <= s.date_order.date() <= last_day);
				total = sum([s.amount_total for s in obj]);
			data[names[i]] = total;
			if maximum < total:
				maximum = total;
			first_day = last_day+datetime.timedelta(days=1);
		maximum = self.roundup(maximum) if maximum else 400;
		return {'data' : data, 
			'max' : maximum};



	@http.route(['/_set_filter_for_table'],type="json", auth="public", website=True)
	def _set_filter_for_table(self,index, **kw):
		request.env['res.users'].sudo().browse(request.env.user.id).filt = int(index);
		return 0;


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


	@http.route(['/_get_product_ids'],type="json", auth="public", website=True)
	def _get_product_ids(self,index, **kw):
		user = request.env.user.id;
		data = [];
		if 'sale.order' in request.env:
			sos = request.env['sale.order'].sudo().search([("user_id",'=',user),('state','=','sale')]);
			sos = self.get_filtered_obj(sos,int(index),'orders');
		else:
			sos = [];
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
		temp = ["sold_id_%s"%(i) for i in temp.keys()];
		data.append(temp);
		if 'purchase.order' in request.env:
			pos = request.env['purchase.order'].sudo().search([("user_id",'=',user),('state','=','purchase')]);
			pos = self.get_filtered_obj(pos,int(index),'orders');
		else:
			pos = [];
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
		temp = ["purchase_id_%s"%(i) for i in temp.keys()];
		data.append(temp);
		return data;


	def roundup(self,x):
		return int(math.ceil(x / 1000.0)) * 1000;

	def string_formatted(self,x):
		if x.find('(') == -1:
			return x[0:];
		else:
			return x[0:x.find('(')];


	@http.route(['/_get_chart_data/products'],type="json", auth="public", website=True)
	def _get_filtered_products(self,index, **kw):
		index = int(index);
		i = index-1;
		user = request.env.user.id;
		data = [];
		if 'sale.order' in request.env:
			sos = request.env['sale.order'].sudo().search([("user_id",'=',user),('state','=','sale')]);
			sos = self.get_filtered_obj(sos,index,'orders');
		else:
			sos = [];
		if 'purchase.order' in request.env:
			pos = request.env['purchase.order'].sudo().search([("user_id",'=',user),('state','=','purchase')]);
			pos = self.get_filtered_obj(pos,index,'orders');
		else:
			pos = [];
		temp = {}
		if len(sos):
			for so in sos:
				for line in so.order_line:
					if line.product_id.id in temp.keys():
						temp[line.product_id.id][1] += line.product_uom_qty * line.price_unit;
					else:
						temp[line.product_id.id] = [self.string_formatted(line.product_id.name),line.product_uom_qty * line.price_unit];
		temp = dict(sorted(temp.items(), key=lambda item: item[1][1] ,reverse=True));
		if len(temp.keys()) > 10:
			temp = dict(list(temp.items())[0:10]);
		ind = 10;
		tempt = {};
		for rKey in temp.keys():
			tempt[ind] = temp[rKey];
			ind -= 1;
		temp = tempt;
		del(tempt);
		maximum = self.roundup(list(temp.items())[0][1][1]) if len(list(temp.items())) else 400;
		data.append({"data" : temp, "max" : maximum,});
		temp = {}
		if len(pos):
			for po in pos:
				for line in po.order_line:
					if line.product_id.id in temp.keys():
						temp[line.product_id.id][1] += line.product_qty * line.price_unit;
					else:
						temp[line.product_id.id] = [self.string_formatted(line.product_id.name),line.product_qty * line.price_unit];
		temp = dict(sorted(temp.items(), key=lambda item: item[1][1] ,reverse=True));
		if len(temp.keys()) > 10:
			temp = dict(list(temp.items())[0:10]);
		ind = 10;
		tempt = {};
		for rKey in temp.keys():
			tempt[ind] = temp[rKey];
			ind -= 1;
		temp = tempt;
		del(tempt);
		maximum = self.roundup(list(temp.items())[0][1][1]) if len(list(temp.items())) else 400;
		data.append({"data" : temp, "max" : maximum,});
		return data;


class SaleCustomerPortal(CustomerPortal):

	@http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
	def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		SaleOrder = request.env['sale.order']

		domain = [
		    ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
		    ('state', 'in', ['sent', 'cancel','draft'])
		]

		searchbar_sortings = {
		    'date': {'label': _('Order Date'), 'order': 'date_order desc'},
		    'name': {'label': _('Reference'), 'order': 'name'},
		    'stage': {'label': _('Stage'), 'order': 'state'},
		}

		if not sortby:
			sortby = 'date'
		sort_order = searchbar_sortings[sortby]['order']

		if date_begin and date_end:
			domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

		quotation_count = SaleOrder.search_count(domain)
		pager = portal_pager(
		    url="/my/quotes",
		    url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
		    total=quotation_count,
		    page=page,
		    step=self._items_per_page
		)
		quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
		request.session['my_quotations_history'] = quotations.ids[:100]

		values.update({
		    'date': date_begin,
		    'quotations': quotations.sudo(),
		    'page_name': 'quote',
		    'pager': pager,
		    'default_url': '/my/quotes',
		    'searchbar_sortings': searchbar_sortings,
		    'sortby': sortby,
		})
		return request.render("sale.portal_my_quotations", values)

	def _prepare_home_portal_values(self, counters):
		res = super(SaleCustomerPortal,self)._prepare_home_portal_values(counters)
		partner = request.env.user.partner_id

		SaleOrder = request.env['sale.order']
		if 'quotation_count' in counters:
			res['quotation_count'] = SaleOrder.search_count([
			    ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
			    ('state', 'in', ['sent', 'cancel','draft'])
			])

		return res