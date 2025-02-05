/* @odoo-module */

import { BryntumGanttController } from "@bryntum_gantt/js/bryntum_gantt_controller";
import { BryntumGanttRenderer } from "@bryntum_gantt/js/bryntum_gantt_renderer";
import { BryntumArchParser } from "@bryntum_gantt/js/bryntum_arch_parser";
import { registry } from "@web/core/registry";
export const BryntumGantt = {
    type: "BryntumGantt",
    display_name: "Bryntum Gantt",
    icon: "fa fa-th-list",
    multiRecord: true,
    searchMenuTypes: ["filter", "favorite"],
    Controller: BryntumGanttController,
    Renderer: BryntumGanttRenderer,
    ArchParser: BryntumArchParser,
    props: (genericProps, view) => {
        const { arch, relatedModels, resModel } = genericProps;
        const archInfo = new view.ArchParser().parse(arch, relatedModels, resModel);
        console.log('genericProps--',genericProps)
        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
        };
    },
};

registry.category("views").add("BryntumGantt", BryntumGantt);
