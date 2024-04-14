/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
	async _processData(loadedData) {
		await super._processData(...arguments);
		var result = loadedData['pos.kitchen.screen.config']
		var self = this
		self.db.pos_screen_data = {};
		self.db.recent_notifications = [];
		result.forEach(data => {
			if (data && (data.pos_config_ids.indexOf(self.config.id) != -1)) {
				self.db.pos_screen_data[data.id] = data;
			}
		});
	},
	update_token_number() {
		var self = this;
		return self.orm.silent.call('pos.order', 'get_token_number').then(function (data) {
			if (data) self.db.next_order_token = data;
			else self.db.next_order_token = '#0000';
		});
	},
	update_kitchen_orders() {
		var self = this;
		if (self.db.kitchen_order_by_id){
			var promise = self.orm.silent.call('pos.order', 'update_order_progress', [Object.keys(self.db.kitchen_order_by_id)]).then(function (data) {
				if (data) {
					data.forEach(obj => {
						self.db.kitchen_order_by_id[obj.id.toString()]['order_progress'] = obj.order_progress;
					});
				}
			});
		}
		return promise
	},
	_save_to_server(orders, options) {
		var self = this;
		return super._save_to_server(orders, options).then(function (return_dict) {
			if (return_dict) {
				return_dict.forEach(data => {
					if (data.orders != null) {
						data.orderlines.forEach(function (orderline) {
							if (self.db.pos_all_kitchen_order_lines){
								self.db.pos_all_kitchen_order_lines.unshift(orderline);
							}
							self.db.kitchen_line_by_id[orderline.id] = orderline;
						});
						data.orders.forEach(function (order) {
							var order_date = new Date(order['date_order'])
							var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
							order['date_order'] = new Date(utc).toLocaleString();
							if (self.db.pos_screen_data[2] && self.db.pos_screen_data[2].queue_order == 'new2old') {
								self.db.pos_all_kitchen_orders.unshift(order.id);
							} else {
								self.db.pos_all_kitchen_orders.push(order.id);
							}
							self.db.kitchen_order_by_id[order.id] = order;
							if (self.db.kitchen_order_by_id) self.update_kitchen_orders();
						});
						delete data.orders;
						delete data.orderlines;
					}
				});
			}
			return return_dict
		});
	},
    getReceiptHeaderData() {
		if (this.db.next_order_token && this.get_order().validate_order_for_kitchen()) {
			var next_order_token = this.db.next_order_token;
			var new_token = '';
			var token = next_order_token.split("#")[1]
			var new_number = parseInt(token) + 1;
			new_token = "#" + (new_number / 10000).toString().split('.')[1]
			receipt.token_no = new_token;
		}
        return {
            ...super.getReceiptHeaderData(...arguments),
            token_number: new_token,
        };
    },
});

patch(Order.prototype, {
	electronic_payment_in_progress() {
		return this.get_paymentlines().some(function (pl) {
			if (pl.payment_status) {
				return !['done', 'reversed'].includes(pl.payment_status);
			} else return false;
		});
	},
	send_order_button_on_validate() {
		var self = this;
		var pos_categ_ids = [];
		var order = self;
		var is_order_validate = true;
		try {
			if (order) {
				self.orm.silent.call('pos.kitchen.order',  'get_kitchen_order_data', [order.export_as_JSON(), is_order_validate, order.order_changes]
				).then(function (return_dict) {
					order.is_order_sent = true;
					self.add_data_for_updation(return_dict);
				})
			}
		} catch { }
	},
	async update_kitchen_restaurant_orders() {
		var self = this;
		var promise = await self.env.services.orm.call('pos.kitchen.order', 'update_kitchen_order_progress' [Object.keys(self.pos.db.kitchen_order_by_id)]
		).then(function (data) {
			if (data) {
				if (data.progress){
					data.progress.forEach(obj => {
						self.pos.db.kitchen_order_by_id[obj.id.toString()]['order_progress'] = obj.order_progress;
					});
				}
				if(data.order_qtys){
					data.order_qtys.forEach(obj => {
						self.pos.db.kitchen_order_by_id[obj.id.toString()]['total_qtys'] = obj.total_qtys;
						self.pos.db.kitchen_order_by_id[obj.id.toString()]['partner_id'] = obj.partner_id;
					});
				}
				if (data.qtys){
					data.qtys.forEach(obj => {
						if (Object.keys(self.pos.db.kitchen_line_by_id).indexOf(obj.id.toString()) != -1){
							self.pos.db.kitchen_line_by_id[obj.id.toString()]['total_qtys'] = obj.total_qtys;
						}
					});
				}
			}
		});
		return promise;
	},
	add_data_for_updation(data) {
		var self = this;
		if (data) {
			if (data.orders != null) {
				data.orderlines.forEach(function (orderline) {
					self.pos.db.pos_all_kitchen_order_lines.unshift(orderline);
					self.pos.db.kitchen_line_by_id[orderline.id] = orderline;
				});
				data.orders.forEach(function (order) {
					var order_date = new Date(order['date_order'])
					var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
					order['date_order'] = new Date(utc).toLocaleString();

					if (self.pos.db.pos_screen_data && self.pos.db.pos_screen_data.queue_order == 'new2old'){
						self.pos.db.pos_all_kitchen_orders.unshift(order.id);
					} else self.pos.db.pos_all_kitchen_orders.push(order.id);

					self.pos.db.kitchen_order_by_id[order.id] = order;

					if (Object.keys(self.pos.db.kitchen_order_by_id).length){
						self.pos.update_kitchen_restaurant_orders();
					}
				});
				delete data.orders;
				delete data.orderlines;
			}
		}
	},
	get_queue_no() {
		var self = this;
		return self.pos.get_order().token_number;
	},
	export_as_JSON() {
		var self = this;
		var loaded = super.export_as_JSON();
		loaded.is_kitchen_order = self.validate_order_for_kitchen();
		loaded.token_no = self.token_no;
		return loaded;
	},
	add_token_number() {
		var self = this;
		var res = self.orm.silent.call('pos.order', 'get_token_number',).then(function (res) {
			self.pos.get_order().token_no = res;
		}).catch(function (e) {
			console.log("e", e)
		})
		return res;
	},
	validate_order_for_kitchen() {
		var self = this;
		var screen_data = self.pos.db.pos_screen_data;
		var is_kitchen_order = false;
		var pos_categ_ids = [];
		Object.values(self.pos.db.pos_screen_data).forEach(data => {
			pos_categ_ids = pos_categ_ids.concat(data.pos_category_ids);
		});

		if (screen_data && !self.is_return_order) {
			if (screen_data && !pos_categ_ids) is_kitchen_order = true;

			if (!is_kitchen_order){
				self.get_orderlines().forEach(line => {
					if (line.product.pos_categ_ids) {
						line.product.pos_categ_ids.forEach(cat => {
							if (pos_categ_ids && pos_categ_ids.indexOf(cat) != -1) is_kitchen_order = true
						});
					}
				});
			}
		}
		return is_kitchen_order
	},
	export_for_printing() {
		var self = this
		var receipt = super.export_for_printing()
		if (self.pos.db.next_order_token && self.pos.get_order().validate_order_for_kitchen()) {
			var next_order_token = self.pos.db.next_order_token;
			var new_token = '';
			var token = next_order_token.split("#")[1]
			var new_number = parseInt(token) + 1;
			new_token = "#" + (new_number / 10000).toString().split('.')[1]
			receipt.token_no = new_token;
		}
		return receipt
	}
});