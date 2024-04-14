// odoo.define('website_global_search_odoo.product_category_display', function(require) {
odoo.define('website_global_search_odoo.product_category_display', [] , function(require) {
    "use strict";
//     var ajax = require('web.ajax');
//     require('web.dom_ready');
// //        $(window).load(function() {
//     ajax.jsonRpc('/global/search', 'call', {}).then(function(category_data) {
//            $.each(category_data, function (key, value) {
//                 $("#product_list").append($('<option>', {
//                      value: value.id,
//                      text: value.name
//                 }));
//         });
//         $("#product_list").val($(".prob_js_global_search_category").val())
// //        }
//     });

    $.ajax({
                    type: "POST",
                    dataType: 'json',
                    url: '/global/search',
                    contentType: "application/json; charset=utf-8",
                    data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {}}),
                    success: function (category_data) {
               
                            var productList = $("#product_list");

                            category_data['result'].forEach(function (item) {
                                    productList.append($('<option>', {
                                        value: item.id,
                                        text: item.name
                                    }));
                                });
                       
                    }
                });
     $("#product_list").val($(".prob_js_global_search_category").val())
    $('#search_box').val('');
//        });
});
