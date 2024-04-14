/** @odoo-module */

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ProductDetailsPopup } from "@sh_pos_motorcycle/js/ProductDetailsPopup";


patch(ProductCard.prototype, {
    setup() {
        super.setup()
        this.pos = usePos();
        this.popup = useService("popup");
    },
    ClickOnDetails(event) {
        var self = this
        const Product = self.pos.db.get_product_by_id(event)
        var motorcycle_id = Product.motorcycle_ids

        var details = []

        for (const each_motorcycle of motorcycle_id) {
            var res = self.pos.db.get_motorcycle_by_id(each_motorcycle)
            details.push(res)
        }
        let { confirmed } = this.popup.add(ProductDetailsPopup,  {
            details: details
        });
        if (confirmed) {
        } else {
            return;
        }

    }
})
