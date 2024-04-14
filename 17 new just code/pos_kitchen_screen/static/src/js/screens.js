/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(ProductScreen.prototype, {
    setup(){
        super.setup();
        var self = this;
        setInterval(self.fetch_updated_orders, 8000, self);
    },
    fetch_updated_orders(self) {
        var order_ref = [];
        self.pos.orders.forEach(order => {
            order_ref.push(order.name);
        });

        self.orm.call('pos.order', 'fetch_updated_orders', [self.pos.config.id, order_ref]).then(function (res) {
            if (Object.keys(res.orders).length) {
                self.pos.db.recent_notifications.unshift([Object.keys(res.orders)[0], Object.values(res.orders)[0], res.time])
                var html = renderToString('PushNotificationWidget', {
                    'time': res.time,
                    'orders': res.orders
                });
                $('.pos').append(html);
                setTimeout(function () {
                    $('.push_notification').remove();
                    $('.pos').off();
                }, 5000)
            }
            if (res.ref_wise_progress) {
                self.pos.orders.forEach(order => {
                    if (Object.keys(res.ref_wise_progress).indexOf(order.name) != -1){
                        order.order_progress = res.ref_wise_progress[order.name][0];
                    }
                    if (Object.keys(res.ref_wise_progress).indexOf(order.name) != -1){
                        order.token_number = res.ref_wise_progress[order.name][1];
                    }
                });
            }
        }).catch(function (error) {
            console.log('error', error)
        })
    }
});

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        var self = this;
        self.pos.get_order().send_order_button_on_validate();
        super.validateOrder(isForceValidate);
    }
});

export class KitchenScreenWidget extends Component {
    static template = "KitchenScreenWidget";

    setup(){
        super.setup();
        var self = this;
        this.pos = usePos();
        setTimeout(function () {
            var orders = self.pos.db.pos_all_kitchen_orders;
            self.render_list(orders, undefined);
        }, 150);
    }
    render_list(orders, input_txt) {
        var self = this;
        var new_order_data = [];
        if (input_txt != undefined && input_txt != '') {
            var search_text = input_txt.toLowerCase()
            for (var i = 0; i < orders.length; i++) {
                let kitchen_order = self.pos.db.kitchen_order_by_id[orders[i]];
                if (kitchen_order) {
                    if (kitchen_order.partner_id == '') {
                        kitchen_order.partner_id = [0, '-'];
                    }
                    if ((kitchen_order.name && kitchen_order.name.toLowerCase().indexOf(search_text) != -1) || (kitchen_order.pos_reference && kitchen_order.pos_reference.toLowerCase().indexOf(search_text) != -1) || (kitchen_order.kitchen_order_name && kitchen_order.kitchen_order_name.toLowerCase().indexOf(search_text) != -1) || (kitchen_order.order_progress && kitchen_order.order_progress.toLowerCase().indexOf(search_text) != -1) || (kitchen_order.date_order && kitchen_order.date_order.toLowerCase().indexOf(search_text) != -1)) {
                        new_order_data = new_order_data.concat(orders[i]);
                    }
                }
            }
            orders = new_order_data;
        }
        
        orders.forEach(order => {
            self.pos.db.kitchen_order_by_id[order].items = self.pos.db.kitchen_order_by_id[order].total_qtys;
        });

        var contents = $('div.partnerlist-screen.screen')[0].querySelector('.wk-kitchen-list-contents');
        contents.innerHTML = "";
        var wk_orders = orders;
        if (wk_orders && wk_orders.length) {
            for (var i = 0, len = Math.min(wk_orders.length, 1000); i < len; i++) {
                var wk_order = wk_orders[i];
                var orderline_html = renderToString('WkKitchenOrderLine', {
                    env: self.env,
                    order: self.pos.db.kitchen_order_by_id[wk_orders[i]],
                    customer_id: self.pos.db.kitchen_order_by_id[wk_orders[i]].partner_id[0],
                });
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                contents.appendChild(orderline);
            }
        }
    }
    keyup_order_search(event) {
        var orders = this.pos.db.pos_all_kitchen_orders;
        this.render_list(orders, event.target.value);
    }
    clickBack(event) {
        this.pos.showScreen('ProductScreen');
    }
}

export class WkErrorKSPopopWidget extends AbstractAwaitablePopup {
    static template = "WkErrorKSPopopWidget";
    static defaultProps = { body: "" };
}

export class KitchenOrdersButton extends Component {
    static template = "KitchenOrdersButton";

    setup() {
        this.pos = usePos();
    }
    async onclick() {
        var self = this;
        var promise_obj = self.pos.get_order().update_kitchen_restaurant_orders();
        promise_obj.then(function (res) {
            self.pos.showScreen('KitchenScreenWidget', { env: self.env });
        })
    }
}
ProductScreen.addControlButton({
    component: KitchenOrdersButton,
    condition: function () {
        return true;
    },
});

// const PosProductsWidgetControlPanel = (ProductsWidgetControlPanel) => class extends ProductsWidgetControlPanel {
//     click_recent_notification(ev) {
//         var self = this
//         ev.stopPropagation();
//         var html = renderToString('RecentNotificationsTemplate', { 'data': self.env.pos.db.recent_notifications });
//         $('.pos').append(html);
//         $('.pos').on('click', function (e) {
//             e.stopPropagation();
//             $('.push_notification').remove();
//             $('.pos').off();
//         })
//         setTimeout(function () {
//             $('.push_notification').remove();
//             $('.pos').off();
//         }, 3000)
//     }
// }
// Registries.Component.extend(ProductsWidgetControlPanel, PosProductsWidgetControlPanel);