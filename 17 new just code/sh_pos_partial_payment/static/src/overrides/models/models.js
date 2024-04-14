/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    is_paid() {
        if (this.pos.config.enable_partial_payment && this.pos.get_order().to_invoice && this.pos.get_order()?.get_partner()?.not_allow_partial_payment===false) {
            return true;
        } else {
            return super.is_paid(...arguments);
        }
    }
});
