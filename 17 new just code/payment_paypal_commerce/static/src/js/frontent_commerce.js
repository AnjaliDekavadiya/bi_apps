/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

    import publicWidget from "@web/legacy/js/public/public_widget";
    import "@payment/js/payment_form";
    import { _t } from "@web/core/l10n/translation";
    import { jsonrpc } from "@web/core/network/rpc_service";

    publicWidget.registry.PaypalCommerceButton = publicWidget.Widget.extend({

        selector: '#commerce_button',

        loadJsScript: function(url, marchant_ids){
            // Check the DOM to see if a script with the specified url is already there
            var alreadyRequired = ($('script[src="' + url + '"]').length > 0);

            var scriptLoadedPromise = new Promise(function (resolve, reject) {
                if (alreadyRequired) {
                    resolve();
                } else {
                    // Get the script associated promise and returns it after initializing the script if needed. The
                    // promise is marked to be resolved on script load and rejected on script error.
                    var script = document.createElement('script');
                    script.type = 'text/javascript';
                    script.src = url;
                    if(marchant_ids){
                        script.dataset.merchantId = marchant_ids;
                    }
                    script.onload = script.onreadystatechange = function() {
                        if ((script.readyState && script.readyState !== "loaded" && script.readyState !== "complete") || script.onload_done) {
                            return;
                        }
                        script.onload_done = true;
                        resolve(url);
                    };
                    script.onerror = function () {
                        console.error("Error loading file", script.src);
                        reject(url);
                    };
                    var head = document.head || document.getElementsByTagName('head')[0];
                    head.appendChild(script);
                }
            });

            return scriptLoadedPromise;
        },

        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return jsonrpc('/paypal/commerce/sdk/url',
                    {}
                ).then(function(result){
                    if(result){
                        console.log("---",result.url,result.marchant_ids,"-----");
                        return self.loadJsScript(result.url, result.marchant_ids).then(function(){
                        // return ajax.loadJS(url).then(function(){
                            self.commerce_override();
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
            var provider = checked_radio.dataset.provider
            if(provider === 'paypal_commerce'){
                var $tx_url = form.find('input[name="prepare_tx_url"]');
                if ($tx_url.length === 1) {
                    var values = {
                        acquirer_id: parseInt($(checked_radio).data('acquirer-id')),
                        save_token: $('input[name="o_payment_form_save_token"]').checked === true,
                        access_token: form.data('access-token'),
                        success_url: form.data('success-url'),
                        error_url: form.data('error-url'),
                        callback_method: form.data('callback-method'),
                        order_id: form.data('order-id'),
                    }
                    return jsonrpc(
                        $tx_url[0].value,
                        values,
                    ).then(function (result) {
                        var newForm = document.createElement('div');
                        newForm.innerHTML = result;
                        return $(newForm).find('input[name="commerce_order_id"]').val();
                    });
                }
            }
            return {}
        },
        commerce_override: function () {
            var self = this;
            var loader = $('#paypal_commerce_loader');
            paypal.Buttons({
                style: {
                    size: 'small',
                    color: 'blue',
                    shape: 'pill',
                    label:  'pay',
                },
                createOrder: function (data, actions) {
                    var values;
                    return self.order_values().then(function (commerce_order_id){
                        return commerce_order_id
                    });
                },
                onApprove: function (data, actions) {
                    var values = {"order_id" : data.orderID};
                    loader.show();
                    return jsonrpc(
                        "/paypal/commerce/capture/order",
                        values,
                    ).then(function (result) {
                        if (!result) {
                            alert('Sorry, but something went wrong!');
                        }
                        else{
                            loader.hide();
                            window.location.href = window.location.origin + result
                        }
                    });
                },
                onCancel: function (data, actions) {
                    console.log("------onCancel-----------");
                },
                onError: function (error) {
                    // This is not handle in this module because of two reasons:
                    // 1. error object details is not mention in paypal doc.
                    // 2. Page close and page unload trigger onError function of Smart Payment Button.
                    loader.hide();
                    console.log("------onError-------",error,"----");
                    // return alert(error);
                }
            }).render('#commerce_button');
        },
    });

    publicWidget.registry.PaymentForm.include({

        _selectPaymentOption: function () {
            // we need to check sale order and show error
            console.log('working payment')
            var self = this;
            this._super.apply(this, arguments);
            var checked_radio = this.$('input[type="radio"]:checked');
            var error_div = $('.paypal_commerce_error');
            var loader = $('#paypal_commerce_loader');
            if (checked_radio.length !== 1) {
                return;
            }
            checked_radio = checked_radio[0];
            var provider = checked_radio.dataset.providerCode
            if(provider == 'paypal_commerce'){
                $('#o_payment_form_pay').hide();
                loader.show();
                return jsonrpc("/paypal/commerce/order/validate"
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
                        $('#commerce_button').show();
                    }
                });
            }
            else{
                error_div.text("");
                error_div.hide();
                $('#commerce_button').hide();
                $('#o_payment_form_pay').show();
            }
        },

    });

    return publicWidget.registry.PaypalCommerceButton;

