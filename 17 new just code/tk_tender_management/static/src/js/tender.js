/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";
    $(document).ready(function () {
        $("#country_id").on("change", function () {
            var text = "<option value='' selected='selected'>Select State</option>"
            var countryId = $(this).val();
            jsonrpc("/get_state", {
                country_id: countryId
            }).then(function (state_ids) {
                if (state_ids) {
                    for (var key in state_ids) {
                        text = text + '<option value="' + key + '">' + state_ids[key] + '</option>'
                    }
                    $('#state_id').empty().append(text);
                }
            });
        });
    });