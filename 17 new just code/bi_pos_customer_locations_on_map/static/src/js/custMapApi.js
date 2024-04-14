/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { loadJS } from "@web/core/assets";

patch(PosStore.prototype, {
        async setup() {
                await super.setup(...arguments);
                var self = this;
                this.env.services.orm.call(
                        'pos.config',
                        'get_google_map_key',
                        [1]
                ).then(async function (key) {
                        console.log("_____key",key)
                        await loadJS(`https://maps.googleapis.com/maps/api/js?v=3.exp&libraries=places&key=${key}`);
                });

        },
});




