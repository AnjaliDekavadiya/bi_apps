/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    _save_to_server(orders, options) {
        // Make List of Products to download the Gift Voucher
        var order_pos_reference = []
        orders.forEach(function (order) {
            order_pos_reference.push(order.data.name)
        })
        var self = this;
        return super._save_to_server(orders, options).then(async function (return_dict) {
            if (return_dict) {
                if (self.config.print_gift_card) {
                    if (order_pos_reference.length) {
                        const voucer_ids = await self.env.services.orm.silent.call(
                            'pos.order',
                            'get_gift_vouchers',
                            [order_pos_reference],
                        )
                        if (voucer_ids.length) {
                            var i = 0;
                            var interval = setInterval(async function () {
                                if (i < voucer_ids.length) {
                                    await self.env.services.report.doAction('wk_coupons.coupons_report', [voucer_ids[i]])
                                }
                                else {
                                    clearInterval(interval)
                                }
                                i++;
                            }, 1500)
                        }
                    }
                }
                return return_dict
            }
        })
    }
});