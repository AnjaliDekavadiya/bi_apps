/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { OrderListScreen } from "@sh_pos_order_list/apps/screen/order_list_screen/order_list_screen";
import { patch } from "@web/core/utils/patch";

patch(OrderListScreen.prototype, {
    setup() {
        this.popup = useService("popup");
        super.setup();
    },
    sh_appy_search(search) {
        if (search == 'partial'){
            if (this.isSearch && (this.shFilteredOrders && this.shFilteredOrders.length)) {
                return this.shFilteredOrders.filter((rec)=>rec[0].sh_amount_residual > 0)
            } else {
                return Object.values(this.pos.db.pos_order_by_id).filter((rec)=>rec[0].sh_amount_residual > 0)
            }
        }
        return super.sh_appy_search(search)
    },
    pay_pos_order(order_data) {
        
        var self = this;
        if (order_data) {
            if (self.pos.get_order().get_orderlines().length > 0) {
                self.pos.add_new_order()
            }
            var current_order = self.pos.get_order()
            var partial_product = self.pos.db.get_product_by_id(self.pos.config.sh_partial_pay_product_id[0])       
            if (!partial_product){
                this.popup.add(ErrorPopup, {
                    title: _t("Not Found"),
                    body: _t(
                        "Partial product not found please check your configuration or product pos categories"
                    ),
                });
                return
            }
            if (current_order) {
                current_order.is_due_paid = true
                
                if (order_data.partner_id) {
                    current_order.set_partner(self.pos.db.get_partner_by_id(order_data.partner_id));
                }
                current_order.add_product(partial_product, {
                    price: order_data.sh_amount_residual,
                });
                if (order_data.sh_amount_residual) {
                    current_order.sh_due_amount = order_data.amount_paid
                } else {
                    current_order.sh_due_amount = 0.00
                }
                current_order.name = order_data.pos_reference;
                current_order.to_invoice = true;
                current_order.pay()
            }
        }
    }
});
