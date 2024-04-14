/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { SelectionReportType } from "@bi_pos_closed_session_reports/app/sessionreportpopup";

export class SessionReport extends Component {
    static template = "bi_pos_closed_session_reports.SessionReport";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.report = useService("report");
    }
    get BiNextScreen() {
        return 'bireceipt';
    }
    async _onClick() {
        if(this.env.services.pos.config.enable_session_report){
            var self = this;
            var pos_session_id = self.env.services.pos.pos_session.id;
            if(this.env.services.pos.config.z_report_selection == 'both'){
                const { confirmed, payload } = await this.popup.add(SelectionReportType, {
                    title: _t("Print Report"),
                });
                if(confirmed){
                    if(payload == 'pdf'){
                        
                        await this.report.doAction('bi_pos_closed_session_reports.action_report_session_z', 
                            [this.env.services.pos.pos_session.id,
                            
                        ]);
                    }
                    if(payload == 'receipt'){
                        this.pos.showScreen(this.BiNextScreen);
                    }
                }
            } else if(this.env.services.pos.config.z_report_selection == 'pdf'){
                await this.report.doAction('bi_pos_closed_session_reports.action_report_session_z', 
                   
                    [this.env.services.pos.pos_session.id,
                   
                ]);
            } else if(this.env.services.pos.config.z_report_selection == 'receipt'){
                this.pos.showScreen(this.BiNextScreen);
            } else{
                alert("Please select the option that which type of report you have to print.")
            }
        }
    }
}

ProductScreen.addControlButton({
    component: SessionReport,
    condition: function() {
            return this.env.services.pos.config.enable_session_report;
        },
});
