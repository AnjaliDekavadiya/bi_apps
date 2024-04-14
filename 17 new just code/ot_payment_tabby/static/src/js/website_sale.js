/** @odoo-module alias=payment_tabby.website_sale**/
import { WebsiteSale } from '@website_sale/js/website_sale';

import { jsonrpc } from "@web/core/network/rpc_service";

WebsiteSale.include({
    init: function () {
        this._super.apply(this, arguments);
        var self = this
        jsonrpc('/payment_tabby/get_credentials', {}).then((tabbyData) => {
            var data = {
              selector: '#tabby', // required, content of tabby Promo Snippet will be placed in element with that selector.
              currency: 'SAR', // required, currency of your product. AED|SAR|KWD|BHD|QAR only supported, with no spaces or lowercase.
              price:parseFloat($('.oe_currency_value')[0].innerText.replace(',','')), // required, price or the product. 2 decimals max for AED|SAR|QAR and 3 decimals max for KWD|BHD.
              installmentsCount: 4, // Optional, for non-standard plans.
              lang: 'en', // Optional, language of snippet and popups, if the property is not set, then it is based on the attribute 'lang' of your html tag.
              source: 'product', // Optional, snippet placement; `product` for product page and `cart` for cart page.
              publicKey: tabbyData['tabby_public_key'], // required, store Public Key which identifies your account when communicating with tabby.
              merchantCode: tabbyData['tabby_merchant_code']  // required
            }
            new TabbyPromo(data);
        });;
    },
})

export default WebsiteSale;
