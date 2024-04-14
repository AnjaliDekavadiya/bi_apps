/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        if (this.pos.config.enable_partial_payment && !this.pos?.get_order()?.is_paid()) {
            alert(this.pos.get_order().get_partner().name + " is not allow to do partial payment.")
        } else if (this.pos.config.enable_partial_payment && !this.pos.get_order().to_invoice && this.pos.get_order().get_partner() && !this.pos.get_order().get_partner().not_allow_partial_payment && !this.pos.get_order().is_paid()) {
            alert("You can not do a partial payment without invoice.")
        }
        super.validateOrder(isForceValidate)
    }
});
