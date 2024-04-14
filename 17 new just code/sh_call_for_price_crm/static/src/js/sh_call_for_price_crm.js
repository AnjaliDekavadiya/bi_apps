/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.WebsiteRequestQuoteOrderSale = publicWidget.Widget.extend({
    selector: '.sh-call-for-price-crm-model',

    events: {
        'click #bttn_save_changes': '_onClickSubmitFormSaveChanges',
    },

    /**
     * @private
     */
    _onClickSubmitFormSaveChanges(e) {
        e.preventDefault();

        jsonrpc("/sale/product_call_for_price", {
            "product_id": $(".product_id").val(),
            "first_name": $('input[name="input_firstname"]').val(),
            "email": $('input[name="input_email"]').val(),
            "contact_no": $('input[name="input_contactno"]').val(),
            "quantity": $('input[name="input_quantity"]').val(),
            "message": $('textarea[name="input_message"]').val(),
        }).then(function (data) {
            if (data == 1) {
                $("#product_call_for_price_modal .closemodel_btn").click();
                $("#bttn_reset").click();
                $("#alertmsg").html('<div class="alert alert-success"><strong>Thank you for information, we will get back to you as soon as possible.</strong></div>');
            } else {
                $("#product_call_for_price_modal .closemodel_btn").click();
                $("#alertmsg").html('<div class="alert alert-danger"><strong>Failure in product call for price.</strong></div>');
            }
        });
        return false;
    },
});

