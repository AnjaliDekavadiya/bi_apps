/* @odoo-module */
// import { SESSION_STATE } from "@im_livechat/embed/common/livechat_service";

import { Messaging } from "@mail/core/common/messaging_service";

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(Messaging.prototype, {

    setup(env, services) {
        super.setup(env, services);
        this.store.products = {};
        this.store.purchases = {};
        this.store.sales = {};
        this.store.invoices = {};
        this.store.contacts = {};
    },

    async initialize() {
        super.initialize();
        var self = this;
        await this.rpc("/web/dataset/call_kw/product.template/search_read", {
            model: 'product.template',
            method: 'search_read',
            args: [],
            domain: [['detailed_type', '=', 'consu']],
            kwargs: {limit: 20}
        }).then(function (res) {
            self.store.products = res;
        }
            // this.initModelsCallback.bind(this)
        );

        await this.rpc("/web/dataset/call_kw/purchase.order/search_read", {
            model: 'purchase.order',
            method: 'search_read',
            args: [],
            kwargs: {limit:20}
        }).then(function (res) {
            self.store.purchases = res;
        });

        await this.rpc("/web/dataset/call_kw/sale.order/search_read", {
            model: 'sale.order',
            method: 'search_read',
            args: [],
            kwargs: {limit:20}
        }).then(function (res) {
            self.store.sales = res;
        });

        await this.rpc("/web/dataset/call_kw/account.move/search_read", {
            model: 'account.move',
            method: 'search_read',
            args: [],
            kwargs: {}
        }).then(function (res) {
            self.store.invoices = res;
        });

        await this.rpc("/web/dataset/call_kw/res.partner/search_read", {
            model: 'res.partner',
            method: 'search_read',
            args: [],
            kwargs: {limit: 20}
        }).then(function (res) {
            self.store.contacts = res;
        });
    },

    initMessagingCallback(data) {
        console.log("Data====", data);
        console.log("store====", this.store);
        // this.store.Thread.update();
        super.initMessagingCallback(data);
    }
});
