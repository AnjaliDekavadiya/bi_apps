/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";


patch(PosStore.prototype, {
    async closePos() {
        if (!this.user.pos_access_close) {
            this.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to backend!'),
            });
        } else {
            await super.closePos();
        }
    },
});


patch(Navbar.prototype, {
    async closeSession() {
        if (!this.pos.user.pos_access_close) {
            await this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to close a session!'),
            });
        } else {
            await super.closeSession();
        }
    },

    onCashMoveButtonClick() {
        if (!this.pos.user.pos_access_cash_move) {
            this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to cash in/out!'),
            });
        } else {
            super.onCashMoveButtonClick();
        }
    },
});


patch(Order.prototype, {
    async pay() {
        if (!this.pos.user.pos_access_payment) {
            await this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to apply payment!'),
            });
        } else {
            await super.pay();
        }
    },
});


patch(ProductScreen.prototype, {
    _setValue(val) {
        var newQty = this.numberBuffer.get() ? parseFloat(this.numberBuffer.get()) : 0;
        var orderLines = !!this.currentOrder ? this.currentOrder.get_orderlines() : undefined;
        if (orderLines !== undefined && orderLines.length > 0) {
            var currentOrderLine = this.currentOrder.get_selected_orderline();
            var currentQty = this.currentOrder.get_selected_orderline().get_quantity();
            var user = this.pos.user;
            if (currentOrderLine && this.pos.numpadMode === 'quantity' && newQty < currentQty && !user.pos_access_decrease_quantity) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: _t('Access Denied'),
                    body: _t('You do not have access to decrease the quantity of an order line!'),
                });
            } else if (currentOrderLine && this.pos.numpadMode === 'quantity' && val === 'remove' && !user.pos_access_delete_orderline) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: _t('Access Denied'),
                    body: _t('You do not have access to delete an order line!'),
                });
            } else {
                super._setValue(val)
            }
        } else {
            super._setValue(val)
        }
    },

    onNumpadClick(buttonValue) {
        var user = this.pos.user;
        if (buttonValue === 'price' && !user.pos_access_price) {
            this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to change price!'),
            });
        } else if (buttonValue === 'discount' && !user.pos_access_discount) {
            this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to apply discount!'),
            });
        } else {
            super.onNumpadClick(buttonValue);
        }
    },
});


patch(TicketScreen.prototype, {
    async onDeleteOrder(order) {
        if (!this.pos.user.pos_access_delete_order) {
            await this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to delete an order!'),
            });
        } else {
            await super.onDeleteOrder(order);
        }
    }
});
