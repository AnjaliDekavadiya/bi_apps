/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import publicWidget from "@web/legacy/js/public/public_widget";
import PaymentForm from '@payment/js/payment_form';
import { loadJS } from "@web/core/assets";

import { _t } from "@web/core/l10n/translation";

function get_payer_data(data_values){
    var payer = {}
    if(!data_values){
        return payer
    }
    if(data_values.billing_first_name || data_values.billing_last_name){
        var name = {}
        if(data_values.billing_first_name){
            name['given_name'] = data_values.billing_first_name
        }
        if(data_values.billing_last_name){
            name['surname'] = data_values.billing_last_name
        }
        payer['name'] = name
    }
    var address = {}
    if(data_values.billing_address_l1){
        address['address_line_1'] = data_values.billing_address_l1
    }
    if(data_values.billing_area2){
        address['admin_area_2'] = data_values.billing_area2
    }
    if(data_values.billing_area1){
        address['admin_area_1'] = data_values.billing_area1
    }
    if(data_values.billing_zip_code){
        address['postal_code'] = data_values.billing_zip_code
    }
    if(data_values.billing_country_code){
        address['country_code'] = data_values.billing_country_code
    }
    payer['address'] = address
    if(data_values.billing_email){
        payer['email_address'] = data_values.billing_email
    }
    if(data_values.billing_phone.match('^[0-9]{1,14}?$')){
        payer['phone'] = {
            phone_type: "MOBILE",
            phone_number: {
                national_number: data_values.billing_phone,
            }
        }
    }
    return payer
}
function get_shipping_data(data_values){
    var shipping = {}
    if(!data_values){
        return shipping
    }
    if(data_values.shipping_partner_name){
        shipping['name'] = {
            full_name: data_values.shipping_partner_name,
        }
    }
    var shipping_address = {}
    if(data_values.shipping_address_l1){
        shipping_address['address_line_1'] = data_values.shipping_address_l1
    }
    if(data_values.shipping_area2){
        shipping_address['admin_area_2'] = data_values.shipping_area2
    }else{
        shipping_address['admin_area_2'] = data_values.billing_address_l1
    }
    if(data_values.shipping_area1){
        shipping_address['admin_area_1'] = data_values.shipping_area1
    }
    if(data_values.shipping_zip_code){
        shipping_address['postal_code'] = data_values.shipping_zip_code
    }
    if(data_values.shipping_country_code){
        shipping_address['country_code'] = data_values.shipping_country_code
    }
    shipping['address'] = shipping_address
    return shipping
}

PaymentForm.include({
    _onClickPaymentOption: function () {
        // we need to check sale order and show error
        var self = this;
        this._super.apply(this, arguments);
        $('#paypal-button').hide();
        var checked_radio = this.$('input[type="radio"]:checked');
        var error_div = $('.paypal_recurring_error');
        var loader = $('#paypal_express_loader');
        if (checked_radio.length !== 1) {
            return;
        }
        checked_radio = checked_radio[0];
        var provider = checked_radio.dataset.provider
        if(provider == 'paypal_express'){
            $('#o_payment_form_pay').hide();
            loader.show();
            return self.rpc("/paypal/recurring/order/validate",{}
            ).then(function (error) {
                loader.hide();
                if(error){
                    self.$('input[type="radio"]:checked').prop('checked', false);
                    error_div.text(error);
                    error_div.show();
                }
                else{
                    error_div.text("");
                    error_div.hide();
                    $('#paypal-button').show();
                }
            });
        }
        else{
            error_div.text("");
            error_div.hide();
            $('#paypal-button').hide();
            $('#o_payment_form_pay').show();
        }
    },
});

publicWidget.registry.PaypalCheckoutButton = publicWidget.Widget.extend({
    selector: '#paypal-button',
    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        this.rpc = this.bindService("rpc");
    },
    willStart: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return self.rpc('/paypal/express/checkout/url',{}
            ).then(function(res){
                if(res){
                    return loadJS(res.url).then(function(){
                        if(res.type == "express"){
                            self.checkout_override();
                        }
                        else{
                            self.recurring_override();
                        }
                    });
                }
            });
        });
    },
    order_values: function () {
        var self = this;
        var form = $('#payment_method').find('form');
        var checked_radio = form.find('input[type="radio"]:checked');
        if (checked_radio.length !== 1) {
        return;
        }
        checked_radio = checked_radio[0];
        var provider = checked_radio.dataset.providerCode;
        if(provider === 'paypal_express'){
            var $tx_url = form.data("transaction-route");
            if ($tx_url.length > 1) {
            var values = {
                'provider_id': $(checked_radio).data("providerId"),
                'payment_method_id':$(checked_radio).data("paymentOptionId"),
                'token_id' :  Number($(checked_radio).data['paymentOptionId']),
                // 'amount':parseFloat(form.data("amount")),
                // 'currency_id': parseInt(form.data("currency-id")),
                // 'partner_id': parseInt(form.data("partner-id")),
                'flow': "redirect",
                'tokenization_requested': false,
                'landing_route': form.data("landing-route"),
                'access_token': form.data("access-token"),
                'csrf_token': odoo.csrf_token,
                }
                return self.rpc($tx_url, values,
                ).then(function (result) {
                    var newform = document.createElement('div');
                    var $newform = $(newform)
                    $newform.append(result["redirect_form_html"]);
                    var values2 = {
                        amount : $newform.find('input[name="amount"]').val(),
                        plan_id: $newform.find('input[name="plan_id"]').val(),
                        reference : $newform.find('input[name="invoice_num"]').val(),
                        currency_code : $newform.find('input[name="currency"]').val(),
                        billing_first_name: $newform.find('input[name="billing_first_name"]').val(),
                        billing_last_name: $newform.find('input[name="billing_last_name"]').val(),
                        billing_phone: $newform.find('input[name="billing_phone"]').val(),
                        billing_email: $newform.find('input[name="billing_email"]').val(),
                        billing_address_l1: $newform.find('input[name="billing_address_l1"]').val(),
                        billing_area1: $newform.find('input[name="billing_area1"]').val(),
                        billing_area2: $newform.find('input[name="billing_area2"]').val(),
                        billing_zip_code: $newform.find('input[name="billing_zip_code"]').val(),
                        billing_country_code: $newform.find('input[name="billing_country_code"]').val(),
                        shipping_partner_name: $newform.find('input[name="shipping_partner_name"]').val(),
                        shipping_address_l1: $newform.find('input[name="shipping_address_l1"]').val(),
                        shipping_area1: $newform.find('input[name="shipping_area1"]').val(),
                        shipping_area2: $newform.find('input[name="shipping_area2"]').val(),
                        shipping_zip_code: $newform.find('input[name="shipping_zip_code"]').val(),
                        shipping_country_code: $newform.find('input[name="shipping_country_code"]').val(),
                };
                    return values2
                });
            }
        }
        return {}
    },
    checkout_override: function () {
        var self = this;
        var loader = $('#paypal_express_loader');
        paypal.Buttons({
            style: {
                size: 'small',
                color: 'blue',
                shape: 'pill',
                label:  'pay',
            },
            createOrder: function(data, actions) {
                loader.show();
                return self.order_values().then(function (values){
                    loader.hide();
                    return actions.order.create({
                        payer: get_payer_data(values),
                        purchase_units: [{
                            amount: {
                                value: values.amount,
                                currency_code: values.currency_code
                            },
                            reference_id: values.reference,
                            shipping: get_shipping_data(values),
                        }],
                    });
                });
            },
            onApprove: function(data, actions) {
                loader.show();
                return actions.order.capture()
                .then(function (details) {
                    self.rpc('/paypal/express/checkout/state', details
                    ).then(function(result){
                        window.location.href = window.location.origin + result
                        loader.hide();
                    });
                });
            },
            onCancel: function (data, actions) {
                loader.show();
                self.rpc('/paypal/express/checkout/cancel', data
                ).then(function(result){
                    window.location.href = window.location.origin + result
                    loader.hide();
                });
            },
            onError: function (error) {
                // This is not handle in this module because of two reasons:
                // 1. error object details is not mention in paypal doc.
                // 2. Page close and page unload trigger onError function of Smart Payment Button.
                loader.hide();
                return alert(error);
            }
        }).render('#paypal-button');
    },
    recurring_override: function() {
        var self = this;
        var loader = $('#paypal_express_loader');
        paypal.Buttons({
            style: {
                size: 'small',
                color: 'blue',
                shape: 'pill',
                label:  'pay',
            },
            createSubscription: async function(data, actions) {
                loader.show();
                return self.order_values().then(function (values){
                    loader.hide();
                    return actions.subscription.create({
                        "plan_id": values.plan_id
                    });
                });
            },
            onApprove: function(data, actions) {
                loader.show();
                var details = {
                    "subscription_id": data.subscriptionID
                }
                self.rpc('/paypal/express/checkout/state', details
                ).then(function(result){
                    window.location.href = window.location.origin + result
                    loader.hide();
                });
            },
            onCancel: function (data, actions) {
                loader.show();
                self.rpc('/paypal/express/checkout/cancel', data
                ).then(function(result){
                    window.location.href = window.location.origin + result
                    loader.hide();
                });
            },
            onError: function (error) {
                // This is not handle in this module because of two reasons:
                // 1. error object details is not mention in paypal doc.
                // 2. Page close and page unload trigger onError function of Smart Payment Button.
                loader.hide();
                return alert(error);
            }
        }).render('#paypal-button');
    },
});

return publicWidget.registry.PaypalCheckoutButton
