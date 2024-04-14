/** @odoo-module */

import { Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Payment.prototype, {
    setup(options) {
        super.setup(...arguments);
        this.covert_change_to_credit = false
        this.used_credit_payment = false
    },
    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.covert_change_to_credit = this.covert_change_to_credit
        json.used_credit_payment = this.used_credit_payment
        return json;
    },
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.covert_change_to_credit = json.covert_change_to_credit
        this.used_credit_payment = json.used_credit_payment
    },
    //@override
    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        return json;
    },
})