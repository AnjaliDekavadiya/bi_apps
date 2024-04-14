/** @odoo-module **/

// import { WebsiteSale } from 'website_sale.website_sale';
import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({
    // selector: '#product_detail_main',
    selector: '.oe_website_sale',
    /**
    * @override
    */
    willStart() {
        this._cod_status_message();
        return Promise.all([this._super.apply(this, arguments)]);
    },

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _cod_status_message: async function () {
        const productId = $("input[name=product_id]").val();
        if (productId) {
            // return this._rpc({
            //     route: '/shop/cod/status',
            //     params: {
            //         product_id: productId,
            //     },
            // }).then(function (data) {
            //     const status = data['staus']
            //     if (!status) {
            //         let para = document.createElement("p");
            //         para.classList.add("alert");
            //         para.classList.add(data['class']);
            //         para.innerText = data['message'];
            //         document.getElementById("website_cash_on_delivery_status_message").appendChild(para);
            //     }
            // });

            const result = await this.rpc("/shop/cod/status", {product_id: productId});
            if (result) {
                const status = result['staus']
                if (!status) {
                    let para = document.createElement("p");
                    para.classList.add("alert");
                    para.classList.add(result['class']);
                    para.innerText = result['message'];
                    document.getElementById("website_cash_on_delivery_status_message").appendChild(para);
                }
            }
        }
    },
});

// odoo.define('website_cash_on_delivery.website_sale', function (require) {
// 'use strict';

// var publicWidget = require('web.public.widget');
// var WebsiteSale = require('website_sale.website_sale');

// publicWidget.registry.WebsiteSale.include({
//     selector: '#product_detail_main',

// 	/**
//      * @override
//      */
//     willStart() {
//         this._cod_status_message();
//         return Promise.all([this._super.apply(this, arguments)]);
//     },

//     /**
//      * @private
//      * @param {MouseEvent} ev
//      */
//     _cod_status_message: function () {
//         const productId = $("input[name=product_id]").val();
//         if (productId) {
//             return this._rpc({
//                 route: '/shop/cod/status',
//                 params: {
//                     product_id: productId,
//                 },
//             }).then(function (data) {
//                 const status = data['staus']
//                 if (!status) {
//                     let para = document.createElement("p");
//                     para.classList.add("alert");
//                     para.classList.add(data['class']);
//                     para.innerText = data['message'];
//                     document.getElementById("website_cash_on_delivery_status_message").appendChild(para);
//                 }
//             });
//         }
//     },
// });
// });