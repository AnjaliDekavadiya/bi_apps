/* @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.isUsercreate = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change #is_create_user': '_onChangeswitch',
    },
    _onChangeswitch: function(ev) {
        $('#is_create_user').change(function() {
            if ($(this).is(':checked')) {
                $('.password_row').show();
                $('input[name="field_required"]').val('phone,name,password,confirm_password');
            } else {
                $('.password_row').hide();
                $('input[name="field_required"]').val('phone,name');
            }
        });
    }
});