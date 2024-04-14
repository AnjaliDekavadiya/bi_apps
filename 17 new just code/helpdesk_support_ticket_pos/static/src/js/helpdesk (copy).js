odoo.define('helpdesk_support_ticket_pos.helpdesk', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var utils = require('web.utils');

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
	selector: '.oe_helpdesk_ticket',
    events: {
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        this._onCustomGetCustomerPosOrder()
        return def;
    },

    _onCustomGetCustomerPosOrder: function () {
        var self = this;
        this._rpc({
            route: "/custom/helpdesk_pos",
            params: {},
        }).then(function (data) {
            self.$('#helpdesk_support_ticket_pos').html(data.html);
        })
    },

});
});