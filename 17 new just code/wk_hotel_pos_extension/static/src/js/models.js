/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    constructor(obj, options) {
        this.booking_id = false;
        this.room_no = false;
    },
    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.booking_id = this.booking_id;
        json.room_no = this.room_no;
        return json;
    },
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.booking_id = json.booking_id;
        this.room_no = json.room_no;
    }
});