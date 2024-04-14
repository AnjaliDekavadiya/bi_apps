/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

// odoo.define('vendor_pricelist_portal.product_comment', function (require) {
// 'use strict';

//     $(document).on("click", ".update_pricelist_details", function () {
//         $('.custom_pricelist_comment').val('');
//     });
//     $(".hide_pricelist_comment_wizard").click(function () {
//         $('.ProductSupplierModal').modal('hide');
//         setTimeout($('.ProductSupplierModal').modal('hide'), 1);
//     });
// });

// require('web.dom_ready');
// var ajax = require('web.ajax');

    $(".hide_pricelist_comment_wizard").on("click", function(ev){
        
        // ajax.jsonRpc("/custom_pricelist/comment", 'call', {
        jsonrpc("/custom_pricelist/comment", {
            'pricelist_id' : $('#custom_pricelist_comment_id').val(),
            'comment': $('.custom_pricelist_comment').val()
        });   
    });
// });