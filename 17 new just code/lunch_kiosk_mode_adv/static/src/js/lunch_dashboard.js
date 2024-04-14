/** @odoo-module */

import { LunchDashboard } from '@lunch/components/lunch_dashboard';
import { LunchUser } from '@lunch/components/lunch_dashboard';
import { LunchKanbanRenderer } from '@lunch/views/kanban';
import { LunchSearchModel } from '@lunch/views/search_model';

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

const { useState, onWillStart, onMounted } = owl;

patch(LunchSearchModel.prototype,{
    setup() {
        super.setup(...arguments);
        this.lunchState = useState({
            locationId: false,
            userId: false,
            kiosk_mode: false,
            kiosk_user_id: false,
        });
    },
});

patch(LunchDashboard.prototype,{
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
    },

    async orderNow() {
        if (!this.canOrder) {
            return;
        }

        await this.lunchRpc('/lunch/pay');
        await this._fetchLunchInfos();

        if (this.env.searchModel.lunchState.kiosk_mode){
            const result = await this.orm.silent.call("lunch.product", "get_lunch_kiosk_mode_action");
            this.actionService.doAction(result.action,{ clearBreadcrumbs: true});
        }
    }
    
});

patch(LunchKanbanRenderer.prototype,{
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");

        onWillStart(async () => {
            const currentController = this.actionService.currentController;
            console.log(currentController && currentController);
            if (currentController && typeof(currentController.props.action) !== 'undefined') {
                this.env.searchModel.lunchState.kiosk_mode = currentController.props.action.kiosk_mode;
            }

            if (currentController && typeof(currentController.props.action) !== 'undefined') {
                this.env.searchModel.lunchState.kiosk_user_id = currentController.props.action.user_id;
            }
            
            if (this.env.searchModel.lunchState.kiosk_mode){
                this.onUpdateKioskUser(this.env.searchModel.lunchState.kiosk_user_id);
            }
        });

        onMounted(async () => {
            const action = await this.orm.silent.call("lunch.product", "get_lunch_kiosk_mode_action");
            const currentController = this.actionService.currentController;
            if (currentController &&  typeof(currentController.action) !== 'undefined'){
                if (currentController.action.xml_id === 'lunch_kiosk_mode_adv.lunch_product_action_order_kiosk' && !this.env.searchModel.lunchState.kiosk_mode){
                    this.actionService.doAction(action.action,{ clearBreadcrumbs: true});
                }
            }
        });

    },

    async onUpdateKioskUser(value) {
        if (!value) {
            return;
        }
        this.env.searchModel.updateUserId(value);
    },

});

patch(LunchUser.prototype,{
    setup() {
        super.setup();
        this.kiosk_mode = this.env.searchModel.lunchState.kiosk_mode;
    },
});
LunchUser.template = 'lunch_kiosk_mode_adv.LunchUser';