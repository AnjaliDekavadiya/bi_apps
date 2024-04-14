/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
import { ShParkingMgmtDashboard } from '@sh_parking_mgmt/views/ParkingKanbanView';

export class ParkingDashBoardKanbanRenderer extends KanbanRenderer {};

ParkingDashBoardKanbanRenderer.components = Object.assign({}, KanbanRenderer.components, {ShParkingMgmtDashboard})
ParkingDashBoardKanbanRenderer.template = 'sh_parking_mgmt.ParkingKanbanView';

export const ParkingDashBoardKanbanView = {
    ...kanbanView,
    Renderer: ParkingDashBoardKanbanRenderer,
};

registry.category("views").add("parking_dashboard_kanban", ParkingDashBoardKanbanView);
