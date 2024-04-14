/** @odoo-module */
    
    
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
   
export class ProductDetailsPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_motorcycle.ProductDetailsPopup";
        setup() {
            super.setup();
            this.pos = usePos();
        } 
    }
