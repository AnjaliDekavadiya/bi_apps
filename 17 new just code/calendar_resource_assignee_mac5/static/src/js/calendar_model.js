/** @odoo-module **/

import { CalendarModel } from "@web/views/calendar/calendar_model";
import { patch } from "@web/core/utils/patch";


patch(CalendarModel.prototype, {
    buildRawRecord(partialRecord, options = {}) {
        const data = super.buildRawRecord(...arguments);

        const fieldMapping = this.meta.fieldMapping;
        if( !!fieldMapping.resourceByAssignee ){
            data.assignee_user_id = partialRecord.resourceId;
        }
        return data
    },

    makeContextDefaults(rawRecord) {
        const context = super.makeContextDefaults(...arguments);

        const fieldMapping = this.meta.fieldMapping;
        if( !!fieldMapping.resourceByAssignee && !!rawRecord.assignee_user_id ){
            context.default_assignee_user_id = rawRecord.assignee_user_id;
        }
        return context
    },

    async updateData(data) {
        await super.updateData(...arguments);

        var filters = JSON.stringify(data.filterSections.assignee_user_id ? data.filterSections.assignee_user_id.filters : []);
        var domain = JSON.stringify(this.meta.domain ? this.meta.domain : []);
        if (!this.assignee_user_filters || this.assignee_user_filters !== filters
                || !this.assignee_user_domain || this.assignee_user_domain !== domain) {
            this.assignee_user_filters = filters;
            this.assignee_user_domain = domain;
            if (!!this.fc) {
                await this.fc.api.refetchResources()
            }
        }
    },
});
