/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';

WebsiteSale.include({
  _onChangeCombination: async function (ev, $parent, combination) {
    var res = this._super.apply(this, arguments);
    $("#msg_div").removeClass("d-none");
    if (combination.loyalty_base == "variant") {
      var total_points = combination.total_points;
      $(".points").text(" " + total_points)
      if ($(".points").html() == ' 0.0') {
        $("#msg_div").addClass("d-none");
      }
    }
    return res;
  },
});