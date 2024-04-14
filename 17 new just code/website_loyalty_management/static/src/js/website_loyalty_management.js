/** @odoo-module **/

import wSaleUtils from "@website_sale/js/website_sale_utils";
import { WebsiteSale } from '@website_sale/js/website_sale';
import { jsonrpc } from "@web/core/network/rpc_service";

WebsiteSale.include({
    events: Object.assign(WebsiteSale.prototype.events, {
        'click ._o_loyality_confimation': '_loyaltyConfirmationModal',
    }),

    start() {
        if (typeof $('#auto_remove').prev().attr('href') == 'string' && $('#auto_remove').prev().data('virtual_source') == 'wk_website_loyalty') {
            location.href = $('#auto_remove').prev().attr('href');
        }
        return this._super.apply(this, arguments);
    },

    _loyaltyConfirmationModal: function (ev) {

        // Cache the current element in a variable
        let $el = $(this);
        jsonrpc('/loyalty/confirmation/')
            .then(function (response) {
                var $modal = $(response['response'].toString());
                $modal.appendTo($('._o_loyality_confimation').parent().parent())
                    .modal('show')
                    .on('hidden.bs.modal', function () {
                        $el.remove();
                    });
            });
    },
});

// Replacement function that extends the original function
function updateCartNavBar(originalFunc) {
    return function (arg) {
        originalFunc.call(this, arg); // Call the original function
        if (arg.Order_loyalty_points) {
            window.location = window.location;
            $('#sale_order_can_make_points').text(` ${arg.Order_loyalty_points} `)
        }
    };
}

// Extend the original function with the replacement behavior
wSaleUtils.updateCartNavBar = updateCartNavBar(wSaleUtils.updateCartNavBar);