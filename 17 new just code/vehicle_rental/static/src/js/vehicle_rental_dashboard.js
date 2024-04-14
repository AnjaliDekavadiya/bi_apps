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

class VehicleRentalDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            fleetVehicleStats: { 'total_vehicle': 0, 'available_vehicle': 0, 'under_maintenance_vehicle': 0 },
            vehicleContractStatus: { 'draft_vehicle': 0, 'in_progress_vehicle': 0, 'return_contract': 0, 'cancel_contract': 0 }
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });

        onWillStart(async () => {
            let vehicleRentalData = await this.orm.call('vehicle.rental.dashboard', 'get_vehicle_rental_dashboard', []);
            if (vehicleRentalData) {
                this.state.fleetVehicleStats = vehicleRentalData;
                this.state.vehicleContractStatus = vehicleRentalData;
            }
        });
        onMounted(() => {

        })
    }

    viewFleetVehicleDetails(status) {
        let domain, context;
        let fleetState = this.getFleetState(status);
        if (status === 'all') {
            domain = []
        } else {
            domain = [['status', '=', status]]
        }
        context = {'create': false}
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: fleetState,
            res_model: 'fleet.vehicle',
            view_mode: 'kanban',
            views: [[false, 'list'], [false, 'form'], [false, 'kanban']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getFleetState(status) {
        let fleetState;
        if (status === 'all') {
            fleetState = 'Vehicles'
        } else if (status === 'available') {
            fleetState = 'Available Vehicles'
        } else if (status === 'in_maintenance') {
            fleetState = 'Under Maintenance Vehicles'
        }
        return fleetState;
    }

    viewVehicleContractStatus(status) {
        let domain, context;
        let contracts = this.getContractState(status);
        if (status === 'all') {
            domain = []
        } else {
            domain = [['status', '=', status]]
        }
        context = { 'create': false }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: contracts,
            res_model: 'vehicle.contract',
            view_mode: 'kanban',
            views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'calendar'], [false, 'pivot'], [false, 'activity'], [false, 'search']],
            target: 'current',
            context: context,
            domain: domain,
        });
    }

    getContractState(status) {
        let contracts;
        if (status === 'all') {
            contracts = 'Contracts'
        } else if (status === 'b_in_progress') {
            contracts = 'In Progress Contracts'
        } else if (status === 'c_return') {
            contracts = 'Return Contracts'
        } else if (status === 'd_cancel') {
            contracts = 'Cancel Contracts'
        }
        return contracts;
    }

}
VehicleRentalDashboard.template = "vehicle_rental.rental_dashboard";
registry.category("actions").add("vehicle_rental_dashboard", VehicleRentalDashboard);