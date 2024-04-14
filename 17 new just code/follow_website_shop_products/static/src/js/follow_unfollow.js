/** @odoo-module alias=follow_website_shop_products.follow_unfollow **/

// odoo.define('follow_website_shop_products.follow_unfollow', function (require) {
// "use strict";
//     require('web.dom_ready');
    
// var publicWidget = require('web.public.widget');
// var ajax = require('web.ajax');

// var config = require('web.config');
// var VariantMixin = require('website_sale.VariantMixin');
// var wSaleUtils = require('website_sale.utils');
// const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
// require("web.zoomodoo");
// const {extraMenuUpdateCallbacks} = require('website.content.menu');
// const dom = require('web.dom');
// const { cartesian } = require('@web/core/utils/arrays');
// const { ComponentWrapper } = require('web.OwlCompatibility');
// const { ProductImageViewerWrapper } = require("@website_sale/js/components/website_sale_image_viewer");

import publicWidget from '@web/legacy/js/public/public_widget';
import { jsonrpc } from "@web/core/network/rpc_service";

    publicWidget.registry.portalFollow = publicWidget.Widget.extend({
        selector: '.o_website_form_follow_custom',
        events: {
            'click button#follow_custom': '_onFollowProductCustom',
            'click button#unfollow_custom': '_onUnfollowProductCustom'
        },
        start: function(){
            var partner_id = $('#custom_partner_id').val();
            var product_id = $('#custom_product_id').val();
            // ajax.jsonRpc("/follow/get/history_custom", 'call', {
            jsonrpc("/follow/get/history_custom", {
                'partner_id': partner_id,
                'product_id':product_id,
            }).then(function (data) {
                $('.o_website_form_follow_custom').html(data.follow_btn);
                $('.o_website_form_follow_custom').removeClass('o_hidden');
            });
            return this._super.apply(this, arguments);
        },
        _onFollowProductCustom: function(ev){
            var partner_id = $('#custom_partner_id').val();
            var product_id = $('#custom_product_id').val();
            // ajax.jsonRpc("/follow/history_custom", 'call', {
            jsonrpc("/follow/history_custom", {
                'partner_id': partner_id,
                'product_id':product_id,
            }).then(function (data) {
                $('.o_website_form_follow_custom').html(data.follow_btn);
                $('.o_website_form_follow_custom').removeClass('o_hidden');
            });
        },
//                $('.o_website_form_follow_custom').load(location.href+" .o_website_form_follow_custom>*","");

        _onUnfollowProductCustom: function(ev){
            var partner_id = $('#custom_partner_id').val();
            var product_id = $('#custom_product_id').val();
            // ajax.jsonRpc("/unfollow/history_custom", 'call', {
            jsonrpc("/unfollow/history_custom", {
                'partner_id': partner_id,
                'product_id':product_id,
            }).then(function (data) {
                $('.o_website_form_follow_custom').html(data.follow_btn)
                $('.o_website_form_follow_custom').removeClass('o_hidden')
//                $('.o_website_form_follow_custom').load(location.href+" .o_website_form_follow_custom>*","");
            });
        },
    });
// });
    
