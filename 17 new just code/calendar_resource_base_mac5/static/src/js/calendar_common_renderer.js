/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";
import { useCalendarPopover, useClickHandler } from "@web/views/calendar/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { useEffect } from "@odoo/owl";
import { useFullCalendar } from "./hooks";

import { onMounted } from "@odoo/owl";


patch(CalendarCommonRenderer.prototype, {
    setup() {
        // MODIFIED: Uses different fullcalendar with resource
        this.fc = useFullCalendar("fullCalendar", this.options);
        // END
        this.click = useClickHandler(this.onClick, this.onDblClick);
        this.popover = useCalendarPopover(this.constructor.components.Popover);
        this.onWindowResizeDebounced = useDebounced(this.onWindowResize, 200);

        onMounted(() => {
            if (this.props.model.scale === "day" || this.props.model.scale === "week") {
                //Need to wait React
                browser.setTimeout(() => {
                    this.fc.api.scrollToTime("06:00:00");
                }, 0);
            }
        });

        useEffect(() => {
            this.updateSize();
        });

        // ADDED: Fullcalendar in models
        this.props.model.fc = this.fc;
        // END
    },

    get options() {
        const options = super.options;

        const fieldMapping = this.props.model.fieldMapping;
        if (!!fieldMapping.resourceType) {
            options.plugins.push('timeline');
            options.plugins.push('resourceDayGrid');
            options.plugins.push('resourceTimeGrid');
            options.plugins.push('resourceTimeline');
            options.schedulerLicenseKey = fieldMapping.schedulerLicenseKey;

            const scale = this.props.model.scale;
            let scalesInfo;
            if (fieldMapping.resourceType === 'daygrid') {
                scalesInfo = {
                    day: 'resourceDayGridDay',
                    week: 'resourceDayGridWeek',
                    month: 'resourceDayGridMonth',
                };
            } else if (fieldMapping.resourceType === 'timegrid') {
                scalesInfo = {
                    day: 'resourceTimeGridDay',
                    week: 'resourceTimeGridWeek',
                };
            } else if (fieldMapping.resourceType === 'timeline') {
                scalesInfo = {
                    day: 'resourceTimelineDay',
                    week: 'resourceTimelineWeek',
                    month: 'resourceTimelineMonth',
                };

                if (scale === 'week') {
                    options.columnHeaderFormat = 'ddd D';
                    options.slotDuration = {'days': 1};
                    options.slotLabelFormat = [{
                        weekday: 'short',
                        month: 'numeric',
                        day: 'numeric',
                    }];
                } else if (scale === 'month') {
                    options.columnHeaderFormat = 'dddd';
                    options.slotDuration = {'days': 1};
                    options.slotLabelFormat = [{
                        day: 'numeric',
                        weekday: 'narrow',
                    }];
                }
            } else {
                scalesInfo = {
                    day: 'timelineDay',
                    week: 'timelineWeek',
                    month: 'timelineMonth',
                };
            }

            options.defaultView = scalesInfo[scale]
        }
        return options;
    },

    onClick(info) {
        const fieldMapping = this.props.model.fieldMapping;
        if (fieldMapping.resourceType === 'timeline') {
            this.openPopover(info.el, this.props.model.records[info.event.id]);
            this.highlightEvent(info.event, "o_timeline_custom_highlight");
        } else {
            super.onClick(...arguments);
        }
    },

    onEventRender(info) {
        const fieldMapping = this.props.model.fieldMapping;
        if (fieldMapping.resourceType === 'timeline') {
            const { el, event } = info;
            el.querySelector(".fc-title-wrap").classList.add("fc-content")
        }

        super.onEventRender(...arguments);

        this.updateWidth();
    },

    fcEventToRecord(event) {
        const res = super.fcEventToRecord(...arguments);

        const fieldMapping = this.props.model.meta.fieldMapping;
        if( !!fieldMapping.resourceType && !!event._def && !!event._def.resourceIds ){
            var resource = fieldMapping.resources[parseInt(event._def.resourceIds[0])]
            res.resourceId = resource ? resource.id : false;
        } else if ( !!fieldMapping.resourceType && !!event.resource
                    && !!event.resource._resource && !!event.resource._resource.id ){
            var resource = fieldMapping.resources[parseInt(event.resource._resource.id)]
            res.resourceId = resource ? resource.id : false;
        }
        return res;
    },

    onEventMouseEnter(info) {
        const fieldMapping = this.props.model.fieldMapping;
        if (fieldMapping.resourceType === 'timeline') {
            this.highlightEvent(info.event, "o_timeline_custom_highlight");
        } else {
            super.onEventMouseEnter(...arguments);
        }
    },

    onEventMouseLeave(info) {
        const fieldMapping = this.props.model.fieldMapping;
        if (fieldMapping.resourceType === 'timeline') {
            if (!info.event.id) {
                return;
            }
            this.unhighlightEvent(info.event, "o_timeline_custom_highlight");
        } else {
            super.onEventMouseLeave(...arguments);
        }
    },

    onEventDragStart(info) {
        const fieldMapping = this.props.model.fieldMapping;
        if (fieldMapping.resourceType === 'timeline') {
            info.el.classList.add(info.view.type);
            this.fc.api.unselect();
            this.highlightEvent(info.event, "o_timeline_custom_highlight");
        } else {
            super.onEventDragStart(...arguments);
        }
    },

    onEventResizeStart(info) {
        const fieldMapping = this.props.model.fieldMapping;
        if (fieldMapping.resourceType === 'timeline') {
            this.fc.api.unselect();
            this.highlightEvent(info.event, "o_timeline_custom_highlight");
        } else {
            super.onEventResizeStart(...arguments);
        }
    },

    updateWidth() {
        if (!!this.fc && !!this.fc.el) {
            const resources = this.props.model.meta.fieldMapping.resources;
            if (!!resources) {
                var width_day = 100;
                var width_week = 100;
                var width_month = 100;
                for( var count=1; count < Object.keys(resources).length+1; count++){
                    if( count > 1 ){
                        width_month += 100
                    }
                    if( count > 3 ){
                        width_week += 33
                    }
                    if( count > 5 ){
                        width_day += 20
                    }
                }

                for (const el of this.fc.el.querySelectorAll('.fc-resourceTimeGridDay-view')) {
                    el.style.width = width_day.toString()+'%';
                }
                for (const el of this.fc.el.querySelectorAll('.fc-resourceTimeGridWeek-view')) {
                    el.style.width = width_week.toString()+'%';
                }
                for (const el of this.fc.el.querySelectorAll('.fc-resourceTimeGridMonth-view')) {
                    el.style.width = width_month.toString()+'%';
                }
            }
        }
    },
});
