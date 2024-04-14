/** @odoo-module **/

import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";


patch(CalendarCommonRenderer.prototype, {
    get options() {
        const options = super.options;

        var self = this;
        const model = this.props.model;
        const meta = model.meta;
        const fieldMapping = meta.fieldMapping;

        if( !!fieldMapping.resourceByAssignee && meta.resModel === 'calendar.event' ){
            options['refetchResourcesOnNavigate'] = true;
            options['resourceOrder'] = 'sequence,title';
            options['resources'] = function( fetchInfo, successCallback, failureCallback ){
                const data = model.data;
                const filters = data.filterSections.assignee_user_id && data.filterSections.assignee_user_id.filters;
                model.orm.call('res.users', 'get_assignee_resources', [meta.domain, data.range.start, data.range.end, filters]).then(function( resources ){
                    fieldMapping.resources = {};
                    for( var i=0; i < resources.length; i++ ){
                        fieldMapping.resources[resources[i].id] = resources[i];
                    }
                    self.updateWidth(resources);
                    successCallback(resources);
                })
            };
        }
        return options;
    },

    convertRecordToEvent(record) {
        const res = super.convertRecordToEvent(...arguments);

        const fieldMapping = this.props.model.meta.fieldMapping;
        if( !!fieldMapping.resourceByAssignee ){
            res.resourceId = !!record.rawRecord.assignee_user_id ? record.rawRecord.assignee_user_id[0].toString() : false;
        }
        return res;
    },
});
