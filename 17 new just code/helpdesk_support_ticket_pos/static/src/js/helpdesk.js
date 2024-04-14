/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";

import publicWidget from "@web/legacy/js/public/public_widget";
// import { rpc } from "@web/core/rpc";


// odoo.define('helpdesk_support_ticket_pos.helpdesk', function (require) {
// 'use strict';

// var publicWidget = require('web.public.widget');
// var utils = require('web.utils');

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
	selector: '.oe_helpdesk_ticket',
    events: {
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },
    
    start: function () {
        var def = this._super.apply(this, arguments);
        this._onCustomGetCustomerPosOrder();
        return def;
    },

    _onCustomGetCustomerPosOrder: async function () {
        var self = this;
        // this._rpc({
        //     route: "/custom/helpdesk_pos",
        //     params: {},
        // }).then(function (data) {
        //     self.$('#helpdesk_support_ticket_pos').html(data.html);
        // })

        const result = await this.rpc("/custom/helpdesk_pos", {});
        if (result) {
            self.$('#helpdesk_support_ticket_pos').html(result.html);
        }
    },

});
// });