/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { SelectionSession } from "@bi_pos_closed_session_reports/app/selectionpopup";

export class ZReport extends Component {
    static template = "bi_pos_closed_session_reports.ZReport";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.report = useService("report");
    }
   async onClick() {
        var self = this;
        const { confirmed, payload } = await this.popup.add(SelectionSession, {
            title: _t("Posted Session Report"),
        });
        if(confirmed){
            await this.report.doAction('bi_pos_closed_session_reports.action_report_session_z', 
                   
                    [payload,
                   
                ]);
            
        }
    }
}

ProductScreen.addControlButton({
    component: ZReport,
    condition: function() {
            return this.env.services.pos.config.allow_posted_session_report;
        },
});
