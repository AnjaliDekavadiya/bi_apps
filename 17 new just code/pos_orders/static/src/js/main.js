/** @odoo-module */

import { Component } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import { PosDB } from "@point_of_sale/app/store/db";
import { onMounted } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { renderToString } from "@web/core/utils/render";
import { registry } from "@web/core/registry";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.db._loadPosOrders(loadedData['pos.order'])
        this.db._loadPosOrderLines(loadedData['pos.order.line'])
    },
    _save_to_server(orders, options) {
        var self = this;
        return super._save_to_server(...arguments).then(function (return_dict) {
            if (return_dict) {
                return_dict.forEach(data => {
                    if (data.orders != null) {
                        data.orders.forEach(function (order) {
                            if (order.existing) {
                                self.db.pos_all_orders.forEach(function (order_from_list) {
                                    if (order_from_list.id == order.original_order_id){
                                        order_from_list.return_status = order.return_status
                                    }
                                });
                            } else {
                                var order_date = new Date(order['date_order'])
                                var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
                                order['date_order'] = new Date(utc).toLocaleString();
                                self.db.pos_all_orders.unshift(order);
                                self.db.order_by_id[order.id] = order;
                            }
                        });
    
                        data.orderlines.forEach(function (orderline) {
                            if (orderline.existing) {
                                var target_line = self.db.line_by_id[orderline.id];
                                target_line.line_qty_returned = orderline.line_qty_returned;
                            } else {
                                self.db.pos_all_order_lines.unshift(orderline);
                                self.db.line_by_id[orderline.id] = orderline;
                            }
                        });
    
                        if (self.db.all_payments){
                            data.payments.forEach(function (payment) {
                                self.db.all_payments.unshift(payment);
                                self.db.payment_by_id[payment.id] = payment;
                            });
                        }
                        delete data.orders;
                        delete data.orderlines;
                        delete data.payments;
                    }
                });
            }
            return return_dict
        });
    }
});

patch(PosDB.prototype, {
    _loadPosOrders: function (orders) {
        var self = this;
        self.pos_all_orders = orders;
        self.order_by_id = {};

        orders.forEach(function (order) {
            var order_date = new Date(order['date_order']);
            var utc = order_date.getTime() - (order_date.getTimezoneOffset() * 60000);
            order['date_order'] = new Date(utc).toLocaleString();
            self.order_by_id[order.id] = order;
        });
    },
    _loadPosOrderLines: function (lines) {
        var self = this;
        self.pos_all_order_lines = lines;
        self.line_by_id = {};

        lines.forEach(function (line) {
            self.line_by_id[line.id] = line;
        });
    }
});

patch(PartnerLine.prototype, {
    async click_all_orders(event) {
        this.env.services.pos.showTempScreen('OrdersScreenWidget', { 'customer_id': this.props.partner.id });
    }
});

export class AllOrdersButton extends Component {
    static template = "pos_orders.AllOrdersButton";

    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
    }
    async onClick() {
        var self = this;
        var order_ids = [];

        self.pos.db.pos_all_orders.forEach(function (all_orders) {
            order_ids.push(all_orders.id)
        });
        try {
            const records = this.orm.call('pos.order', 'get_all_orders', [{
                    "config_id": self.pos.config.id,
                    "current_order": order_ids,
                    "session_name": self.pos.pos_session.name
            }]);
            records.forEach(function (orders) {
                if (orders.name) {
                    if (!order_ids.includes(orders.id)) {
                        self.pos.db.pos_all_orders.unshift(orders);
                        self.pos.db.order_by_id[orders.id] = orders;
                    }
                }else if (orders.amount) {
                    self.pos.db.all_payments.unshift(orders);
                    self.pos.db.payment_by_id[orders.id] = orders;
                }else {
                    Object.keys(orders).forEach(lines => {
                        self.pos.db.pos_all_order_lines.unshift(orders[lines]);
                        self.pos.db.line_by_id[orders[lines].id] = orders[lines];
                    });
                }
            });
            await self.pos.showTempScreen('OrdersScreenWidget', {});
        } catch (error) {
            await self.pos.showTempScreen('OrdersScreenWidget', {});
        }
    }
}
ProductScreen.addControlButton({
    component: AllOrdersButton,
    condition: function () {
        return true;
    },
});

export class OrdersScreenWidget extends Component {
    static template = "pos_orders.OrdersScreenWidget";

    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        onMounted(this.onMounted);
    }
    onMounted(){
        var orders = this.pos.db.pos_all_orders;
        this.render_list(orders, undefined);
    }
    async refresh() {
        var self = this;
        var order_ids = [];

        self.pos.db.pos_all_orders.forEach(function (all_orders) {
            order_ids.push(all_orders.id);
        });

        try {
            const records = await this.orm.call('pos.order', 'get_all_orders', [{
                "current_order": order_ids,
                "session_name": self.pos.pos_session.name,
                "config_id": self.pos.config.id,
            }]);
            records.forEach(function (orders) {
                if (orders.name) {
                    if (!order_ids.includes(orders.id)) {
                        self.pos.db.pos_all_orders.unshift(orders);
                        self.pos.db.order_by_id[orders.id] = orders;
                    }
                } else if (orders.amount) {
                    self.pos.db.all_payments.unshift(orders);
                    self.pos.db.payment_by_id[orders.id] = orders;
                } else {
                    Object.keys(orders).forEach(lines => {
                        self.pos.db.pos_all_order_lines.push(orders[lines]);
                        self.pos.db.line_by_id[orders[lines].id] = orders[lines];
                    });
                }
            });
            var order = self.pos.db.pos_all_orders;
            self.render_list(order);
        }
        catch (error) {
            self.env.services.popup.add('ErrorPopup', {
                'title': _t('Server Error'),
                'body': _t('Check your internet connection and try again.')
            });
        }
    }
    get_customer(customer_id) {
        if (this.props && this.props.customer_id) {
            return this.props.customer_id
        } else {
            return undefined;
        }
    }
    render_list(order, input_txt) {
        var customer_id = this.get_customer();
        var new_order_data = [];

        if (customer_id != undefined) {
            for (var i = 0; i < order.length; i++) {
                if (order[i].partner_id[0] == customer_id) new_order_data = new_order_data.concat(order[i]);
            }
            order = new_order_data;
        }
        if (input_txt != undefined && input_txt != '') {
            var new_order_data = [];
            var search_text = input_txt.toLowerCase();

            for (var i = 0; i < order.length; i++) {
                if (order[i].partner_id == '') {
                    order[i].partner_id = [0, '-'];
                }
                if (((order[i].name.toLowerCase()).indexOf(search_text) != -1) || ((order[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                    new_order_data = new_order_data.concat(order[i]);
                }
            }
            order = new_order_data;
        }
        var contents = $('div.partnerlist-screen.screen')[0].querySelector('.wk-order-list-contents');
        contents.innerHTML = "";

        var wk_orders = order;
        for (var i = 0, len = Math.min(wk_orders.length, 1000); i < len; i++) {
            var orderline_html = renderToString('WkOrderLine', {
                widget: this,
                order: wk_orders[i],
                customer_id: wk_orders[i].partner_id[0],
            });
            var orderline = document.createElement('tbody');
            orderline.innerHTML = orderline_html;
            orderline = orderline.firstChild;
            contents.appendChild(orderline);
        }
    }
    keyup_order_search(event) {
        var orders = this.pos.db.pos_all_orders;
        this.render_list(orders, event.target.value);
    }
    clickBack(event) {
        var self = this;
        if (self.props.customer_id) self.pos.showTempScreen('PartnerListScreen', {});
        else {
            self.props.resolve({ confirmed: false, payload: null });
            self.pos.closeTempScreen();
        }
    }
};
registry.category("pos_screens").add("OrdersScreenWidget", OrdersScreenWidget);
