/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.websiteSaleDelivery = publicWidget.Widget.extend({
  selector: '.oe_website_sale',

  events: {
    'click .whatsapp_checkout': '_onWhatsappCheckoutClick',
  },
  _onWhatsappCheckoutClick: async function(ev) {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: '/shop/cart/clear',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
          'jsonrpc': "2.0",
          'method': "call",
          "params": {}
        }),
        success: function(action) {
          location.reload();
        }
      });
},
});

