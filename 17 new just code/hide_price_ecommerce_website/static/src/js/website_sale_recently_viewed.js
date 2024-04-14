/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";

// odoo.define('hide_price_ecommerce_website.website_sale_recently_viewed', function (require) {

// var core = require('web.core');
// var publicWidget = require('web.public.widget');

// require('website_sale.recently_viewed');

// var _t = core._t;

// publicWidget.registry.productsRecentlyViewedSnippet.include({

publicWidget.registry.productsRecentlyViewedSnippet = publicWidget.Widget.extend({
    xmlDependencies: ['/hide_price_ecommerce_website/static/src/xml/website_sale_recently_viewed.xml'],
    // xmlDependencies: (publicWidget.registry.productsRecentlyViewedSnippet.prototype.xmlDependencies || []).concat(
        // ['/hide_price_ecommerce_website/static/src/xml/website_sale_recently_viewed.xml']
    // ),
})

// })
