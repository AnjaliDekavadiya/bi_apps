/** @odoo-module */

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import { jsonrpc } from "@web/core/network/rpc_service";
import { whenReady } from "@odoo/owl";

whenReady(() => {
    var payment = $("li[name='o_payment_option']");
    if (payment.length > 0) {
        if (payment.length == 1){
            var checked_radio = payment.find('input[type="radio"]:checked')
            var provider = checked_radio[0].dataset.providerCode
            if(provider == 'stripe'){
                payment.find('input[type="radio"]:checked').prop('checked', false)
            }
        }
        $( "li[name='o_payment_option']" ).on( "click", function() {
            var self = $(this);
            var checked_radio = $(this).find('input[type="radio"]:checked');
            var error_div = $('.paypal_stripe_error');
            if (checked_radio.length !== 1) {
                return;
            }
            checked_radio = checked_radio[0];
            var provider = checked_radio.dataset.providerCode
            if(provider == 'stripe'){
                $('#o_payment_submit_button').hide();
                return jsonrpc("/payment_stripe/order/validate"
                ).then(function (error) {
                    if(error){
                        self.find('input[type="radio"]:checked').prop('checked', false);
                        error_div.text(error);
                        error_div.show();
                        const $submitButton = $('button[name="o_payment_submit_button"]');
                        $submitButton.attr('disabled', true);
                    }
                    else{
                        error_div.text("");
                        error_div.hide();
                    }
                });
            }
            else{
                    error_div.text("");
                    error_div.hide();
                }
          } )
    }
});

