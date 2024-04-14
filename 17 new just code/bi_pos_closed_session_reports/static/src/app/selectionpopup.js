/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";


// IMPROVEMENT: This code is very similar to TextInputPopup.
//      Combining them would reduce the code.
export class SelectionSession extends AbstractAwaitablePopup {
    static template = "bi_pos_closed_session_reports.SelectionSession";
    static defaultProps = {
        confirmText: _t("print"),
        cancelText: _t("close"),
        title: "",
        body: "",
    };

    /**
     * @param {Object} props
     * @param {string} props.startingValue
     */
    setup() {
        super.setup();

        this.pos=usePos();
        this.state = useState({ inputValue: this.props.startingValue });
        this.inputRef = useRef("input");
        this.popup = useService("popup");
    }

    confirm_session(){
        var list_of_data = $('.table-data');
        var self = this;
        $.each(list_of_data, function(index, value) {
            var SelectedSession = $(value).find('select').val();
            if(!SelectedSession){
                alert("Please Select Session");
            } else {

                self.props.close({ confirmed: true, payload: SelectedSession });
                
            }
        });
    }
    
    
}
