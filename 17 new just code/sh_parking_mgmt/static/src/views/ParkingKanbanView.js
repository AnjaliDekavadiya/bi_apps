/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart } from "@odoo/owl";

export class ShParkingMgmtDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        this.rpc = useService("rpc");
    }
    async sh_onchange_qr (qr_code){
        const action = await this.orm.call('sh.parking.subslot', 'calculate_check_out_time', [qr_code], {});
        $("#sh_qr_code_no").val(null);
        if (action['res_model']) {
            this.action.doAction(action);
        }
    }
}

ShParkingMgmtDashboard.template = "sh_parking_mgmt.ShParkingMgmtDashboard";


