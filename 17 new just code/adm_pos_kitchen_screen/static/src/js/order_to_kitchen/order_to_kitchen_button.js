/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class SendToKitchenButton extends Component {
    static template = "adm_pos_kitchen_screen.SendToKitchenButton";

    setup() {
        this.pos = usePos();
    }
    get currentOrder() {
        return this.pos.get_order();
    }
    async click() {
        
        this.pos.sendDraftToServer();

    }
}

ProductScreen.addControlButton({
    component: SendToKitchenButton,
    condition: function () {
        return true;
    },
});
