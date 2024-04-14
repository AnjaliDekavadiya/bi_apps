/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";


patch(Order.prototype, {
    isSentToKitchen(orderLineId = false) {
        const prepaCategoryIds = this.pos.orderPreparationCategories;
        const changes = this.getOrderChanges();
        const oldChanges = this.lastOrderPrepaChange;
        var orderLines;

        if (!orderLineId) {
            orderLines = this.get_orderlines();
        } else {
            orderLines = [this.get_orderline(orderLineId)];
        }

        for( var i=0; i < orderLines.length; i++ ){
            const orderLine = orderLines[i];
            if( prepaCategoryIds.size === 0 || this.pos.db.any_of_is_subcategory(orderLine.product.pos_categ_ids, [...prepaCategoryIds]) ){
                const note = orderLine.getNote();
                const lineKey = `${orderLine.uuid} - ${note}`;
                if (!!oldChanges && lineKey in oldChanges && oldChanges[lineKey].quantity != 0) {
                    return oldChanges[lineKey].quantity;
                }
            }
        }

        if (!orderLineId) {
            for( const orderlineIdx in changes.orderlines ){
                const orderLine = changes.orderlines[orderlineIdx];
                if (orderLine.quantity < 0) {
                    return true;
                }
            }
        }
        return false;
    },
});


patch(PosStore.prototype, {
    async closePos() {
        var orders = this.orders;
        var sent_to_kitchen = false;
        for (var i = 0; i < orders.length; i++) {
            sent_to_kitchen = orders[i].isSentToKitchen();
            if( sent_to_kitchen ){
                break;
            }
        }

        if (!this.user.pos_access_close_sent_kitchen && sent_to_kitchen) {
            this.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to backend with orders sent to kitchen but unpaid!'),
            });
        } else {
            await super.closePos();
        }
    },
});


patch(Navbar.prototype, {
    async closeSession() {
        var orders = this.pos.orders;
        var sent_to_kitchen = false;
        for (var i = 0; i < orders.length; i++) {
            sent_to_kitchen = orders[i].isSentToKitchen();
            if( sent_to_kitchen ){
                break;
            }
        }

        if (!this.pos.user.pos_access_close_sent_kitchen && sent_to_kitchen) {
            await this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to close a session with orders sent to kitchen but unpaid!'),
            });
        } else {
            await super.closeSession();
        }
    },
});


patch(ProductScreen.prototype, {
    _setValue(val) {
        var newQty = this.numberBuffer.get() ? parseFloat(this.numberBuffer.get()) : 0;
        var order = this.currentOrder;
        var orderLines = order?.get_orderlines();
        if (orderLines !== undefined && orderLines.length > 0) {
            var currentOrderLine = order.get_selected_orderline();
            var currentQty = order.isSentToKitchen(currentOrderLine.id);
            var user = this.pos.user;
            if (currentOrderLine && this.pos.numpadMode === 'quantity' && !!currentQty && newQty < currentQty && !user.pos_access_decrease_quantity_sent_kitchen) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: _t('Access Denied'),
                    body: _t('You do not have access to decrease the quantity of an order line with current order sent to kitchen but unpaid!'),
                });
            } else if (currentOrderLine && this.pos.numpadMode === 'quantity' && !!currentQty && val === 'remove' && !user.pos_access_delete_orderline_sent_kitchen) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: _t('Access Denied'),
                    body: _t('You do not have access to delete an order line with current order sent to kitchen but unpaid!'),
                });
            } else {
                super._setValue(val)
            }
        } else {
            super._setValue(val)
        }
    },
});


patch(TicketScreen.prototype, {
    async onDeleteOrder(order) {
        var sent_to_kitchen = order.isSentToKitchen();
        if (!this.pos.user.pos_access_delete_order_sent_kitchen && sent_to_kitchen) {
            await this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to delete an order with current order sent to kitchen but unpaid!'),
            });
        } else {
            await super.onDeleteOrder(order);
        }
    }
});
