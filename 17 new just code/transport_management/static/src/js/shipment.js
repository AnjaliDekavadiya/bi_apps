/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class TransportDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            transportStats: {'all': 0, 'pack': 0, 'ship': 0, 'transit': 0, 'done': 0, 'cancel':0 },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        onWillStart(async () => {
            let transportManagementData = await this.orm.call('transport.shipment', 'get_shipment_stats', []);
            if (transportManagementData) {
                this.state.transportStats = transportManagementData;
                console.log(transportManagementData)
            }
        });
        onMounted(() => {

        })
    }

    viewShipmentStats(types) {
        let domain, context;
        let transportState = this.getShipmentState(types);
        if (types === 'all') {
            domain = []
        } else {
            domain = [['status', '=', types]]
        }
        context = {'create': false}
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: transportState,
            res_model: 'transport.shipment',
            view_mode: 'kanban',
             views: [[false, 'kanban'],[false, 'tree'],[false, 'form'], [false, 'activity']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getShipmentState(types) {
        let transportState;
        if (types === 'all') {
            transportState = 'Shipments'
        } else if (types === 'draft') {
            transportState = 'Packing'
        } else if (types === 'ship') {
            transportState = 'Shipped'
        } else if (types === 'in_transit') {
            transportState = 'In Transit'
        } else if (types === 'done') {
            transportState = 'Delivered'
        } else if (types === 'cancel') {
            transportState = 'Cancelled'
        }
        return transportState;
    }

}
TransportDashboard.template = "transport_management.transport_dashboard";
registry.category("actions").add("shipment_dashboard", TransportDashboard);