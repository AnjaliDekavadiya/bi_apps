/** @odoo-module **/

import { CalendarModel } from "@web/views/calendar/calendar_model";
import { patch } from "@web/core/utils/patch";


patch(CalendarModel.prototype, {
    makeFilterAll(previousAllFilter, isUserOrPartner) {
        const result = super.makeFilterAll(...arguments);

        if( !!this.meta.fieldMapping.resourceType && !this.filter_all_not_init && !!isUserOrPartner ){
            this.filter_all_not_init = true;
            result.active = true;
        }
        return result
    },
});
