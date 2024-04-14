/** @odoo-module **/

import { loadCSS, loadJS } from "@web/core/assets";

import {
    onMounted,
    onPatched,
    onWillStart,
    onWillUnmount,
    onWillUpdateProps,
    useComponent,
    useRef,
} from "@odoo/owl";


export function useFullCalendar(refName, params) {
    const component = useComponent();
    const ref = useRef(refName);
    let instance = null;

    function boundParams() {
        const newParams = {};
        for (const key in params) {
            const value = params[key];
            newParams[key] = typeof value === "function" ? value.bind(component) : value;
        }
        return newParams;
    }

    async function loadJsFiles() {
        const files = [
            "/web/static/lib/fullcalendar/core/main.js",
            "/web/static/lib/fullcalendar/interaction/main.js",
            "/web/static/lib/fullcalendar/daygrid/main.js",
            "/web/static/lib/fullcalendar/luxon/main.js",
            "/web/static/lib/fullcalendar/timegrid/main.js",
            "/web/static/lib/fullcalendar/list/main.js",
            "/calendar_resource_base_mac5/static/lib/fullcalendar/timeline/main.js",
            "/calendar_resource_base_mac5/static/lib/fullcalendar/resource-common/main.js",
            "/calendar_resource_base_mac5/static/lib/fullcalendar/resource-daygrid/main.js",
            "/calendar_resource_base_mac5/static/lib/fullcalendar/resource-timegrid/main.js",
            "/calendar_resource_base_mac5/static/lib/fullcalendar/resource-timeline/main.js",
        ];
        for (const file of files) {
            await loadJS(file);
        }
    }
    async function loadCssFiles() {
        await Promise.all(
            [
                "/web/static/lib/fullcalendar/core/main.css",
                "/web/static/lib/fullcalendar/daygrid/main.css",
                "/web/static/lib/fullcalendar/timegrid/main.css",
                "/web/static/lib/fullcalendar/list/main.css",
                "/calendar_resource_base_mac5/static/lib/fullcalendar/timeline/main.css",
                "/calendar_resource_base_mac5/static/lib/fullcalendar/resource-timeline/main.css",
            ].map((file) => loadCSS(file))
        );
    }

    onWillStart(() => Promise.all([loadJsFiles(), loadCssFiles()]));

    onMounted(() => {
        try {
            instance = new FullCalendar.Calendar(ref.el, boundParams());
            instance.render();
        } catch (e) {
            throw new Error(`Cannot instantiate FullCalendar\n${e.message}`);
        }
    });

    let isWeekendVisible = params.isWeekendVisible;
    onWillUpdateProps((np) => {
        isWeekendVisible = np.isWeekendVisible;
    });
    onPatched(() => {
        instance.refetchEvents();
        instance.setOption("weekends", isWeekendVisible);
    });
    onWillUnmount(() => {
        instance.destroy();
    });

    return {
        get api() {
            return instance;
        },
        get el() {
            return ref.el;
        },
    };
}
