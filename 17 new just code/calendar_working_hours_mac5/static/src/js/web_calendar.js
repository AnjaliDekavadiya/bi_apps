/** @odoo-module **/

import { CalendarArchParser } from "@web/views/calendar/calendar_arch_parser";
import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";
import { visitXML } from "@web/core/utils/xml";


patch(CalendarArchParser.prototype, {
    parse(arch, models, modelName) {
        const result = super.parse(...arguments);

        visitXML(arch, (node) => {
            switch (node.tagName) {
                case "calendar": {
                    if (node.hasAttribute('company_wh_data')) {
                        result.fieldMapping.companyWorkingHourData = JSON.parse(node.getAttribute('company_wh_data'));
                    }
                }
            }
        });
        return result
    },
});

patch(CalendarCommonRenderer.prototype, {
    get options() {
        const result = super.options;

        const fieldMapping = this.props.model.fieldMapping;
        if( !!fieldMapping.companyWorkingHourData ){
            if( (fieldMapping.companyWorkingHourData.calendarEventOnly
                    && this.env.searchModel.resModel === 'calendar.event')
                    || !fieldMapping.companyWorkingHourData.calendarEventOnly ){
                result.businessHours = fieldMapping.companyWorkingHourData.businessHours;
                if( fieldMapping.companyWorkingHourData.eventConstraint ){
                    result.eventConstraint = 'businessHours';
                }
                if( fieldMapping.companyWorkingHourData.selectConstraint ){
                    result.selectConstraint = 'businessHours';
                }
            }
        }
        return result;
    },
});
