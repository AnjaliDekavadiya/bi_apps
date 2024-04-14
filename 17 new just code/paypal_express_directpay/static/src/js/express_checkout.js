/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */
import { patch } from "@web/core/utils/patch";
import publicWidget from '@web/legacy/js/public/public_widget';
import { jsonrpc } from "@web/core/network/rpc_service";

import "@payment_paypal_express/js/express_checkout";

// odoo.define('wk_paypal_express_custom.express_checkout_custom', function (require) {
//     "use strict";
    // var ajax = require('web.ajax');
    var page_url = window.location.href

    // var core = require('web.core');
    // var PaymentPaypalExpress = require('payment_paypal_express.express_checkout');
    var type;
    if (page_url.indexOf("/shop/cart") > -1){
        type = "cart"
    }
    else if (page_url.indexOf("/shop/") > -1){
        type = "product"
    }

    // patch(ExpressCheckout.prototype, {

        // setup() {
        //     super.setup();
        //     // Use the nomenclature's separaor regex, else use an impossible one.
        //     // const nomenclatureSeparator = this.nomenclature && this.nomenclature.gs1_separator_fnc1;
        //     // this.gs1SeparatorRegex = new RegExp(nomenclatureSeparator || '.^', 'g');
        // },
        publicWidget.registry.PaypalCheckoutButton.include({

        get_btn_style: function(){
            if (type=="cart" || type=="product"){
                var b_style = {
                    color:   'gold',
                    shape:   'rect',
                    label:   'checkout',
                    size: 'small',
                    height: 34,
                    tagline: false,
                }
                if (type=="cart"){
                    $("#paypal-button").addClass("cart_paypal_button mr-1")
                }
                else if (type == "product"){
                        b_style["height"] = 40;
                        b_style["size"] = 'small';
                        $("#paypal-button").addClass("pro_paypal_button  col-md-9 pl-0 pr-4")
                }
                return b_style

            }else{
                return this._super.apply(this, arguments);
            }
        },
        get_transaction: function(result){
          var self = this;
          return jsonrpc(
                   '/get/paypal/acquirer/details',
                   result,
                  ).then(function (result) {
                      var acquirer_id = result.acquirer_id
                      var values = {
                                'provider_id': parseInt(acquirer_id),
                                'payment_method_id':parseInt(result.payment_method_id),
                                'token_id' :  Number(parseInt(result.payment_method_id)),
                                //   'sale_order' : result.sale_order,
                                //   'currency_id' : result.currency_id,
                                //   'partner_id'   : result.partner_id,
                                  'flow'          : result.flow,
                                  'tokenization_requested' : result.tokenization_requested,
                                  'landing_route': result.landing_route,
                                  'access_token': result.access_token,
                                    'csrf_token': odoo.csrf_token,
                                }
                                console.log('values====',values)
                                var a = '/shop/payment/transaction/'.concat(result.sale_order)
                      return jsonrpc(
                            '/shop/payment/transaction/'.concat(result.sale_order),
                               values,
                              ).then(function (result) {
                                var newForm = document.createElement('div');
                                
                                    newForm.innerHTML = result["redirect_form_html"];
                                    return {
                                          amount : $(newForm).find('input[name="amount"]').val(),
                                          reference : $(newForm).find('input[name="invoice_num"]').val(),
                                          currency_code : $(newForm).find('input[name="currency"]').val(),
                                          billing_first_name: $(newForm).find('input[name="billing_first_name"]').val(),
                                          billing_last_name: $(newForm).find('input[name="billing_last_name"]').val(),
                                          billing_phone: $(newForm).find('input[name="billing_phone"]').val(),
                                          billing_email: $(newForm).find('input[name="billing_email"]').val(),
                                          billing_address_l1: $(newForm).find('input[name="billing_address_l1"]').val(),
                                          billing_area1: $(newForm).find('input[name="billing_area1"]').val(),
                                          billing_area2: $(newForm).find('input[name="billing_area2"]').val(),
                                          billing_zip_code: $(newForm).find('input[name="billing_zip_code"]').val(),
                                          billing_country_code: $(newForm).find('input[name="billing_country_code"]').val(),
                                          shipping_partner_name: $(newForm).find('input[name="shipping_partner_name"]').val(),
                                          shipping_address_l1: $(newForm).find('input[name="shipping_address_l1"]').val(),
                                          shipping_area1: $(newForm).find('input[name="shipping_area1"]').val(),
                                          shipping_area2: $(newForm).find('input[name="shipping_area2"]').val(),
                                          shipping_zip_code: $(newForm).find('input[name="shipping_zip_code"]').val(),
                                          shipping_country_code: $(newForm).find('input[name="shipping_country_code"]').val(),
                                  }
                                  })
                      })
        },
        create_order: function(){
            var self = this;
            var product_id = parseInt($('#paypal-button').closest('.js_product').find('input[name="product_id"]').val());
            var add_qty = parseInt($('#paypal-button').closest('.js_product').find('input[name="add_qty"]').val());
            var csrf_token = parseInt($('#paypal-button').closest('.js_product').find('input[name="csrf_token"]').val());
            var values = {
                'product_id': product_id,
                'add_qty':  add_qty,
                'csrf_token':csrf_token,
                        }
            return jsonrpc(
                    '/get/product/order/details',
                    values,
                    ).then(function (result) {
                        return result
                        })
        },

        order_values: function () {
            var self = this;
            var page_url = window.location.href
            if (page_url.indexOf("/shop/payment") > -1){
                return this._super.apply(this, arguments);
            }
            if(type=="product"){

                return self.create_order().then(function(result){
                  return self.get_transaction(result)
                })
            }else{
              return self.get_transaction()
            }
        },
    })
// })

// });
