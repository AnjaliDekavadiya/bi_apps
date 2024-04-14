/** @odoo-module */

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import publicWidget from "@web/legacy/js/public/public_widget";
    $(document).ready(function(){

    publicWidget.registry.PortalHomeCounters.include({
        /**
         * @override
         */
        _getCountersAlwaysDisplayed() {
            return this._super(...arguments).concat(['my_ad_blocks_count']);
        },
    });

    });