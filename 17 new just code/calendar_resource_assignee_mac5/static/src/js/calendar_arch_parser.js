/** @odoo-module **/

import { CalendarArchParser } from "@web/views/calendar/calendar_arch_parser";
import { patch } from "@web/core/utils/patch";
import { visitXML } from "@web/core/utils/xml";


patch(CalendarArchParser.prototype, {
    parse(arch, models, modelName) {
        const result = super.parse(...arguments);

        visitXML(arch, (node) => {
            switch (node.tagName) {
                case "calendar": {
                    if (node.hasAttribute('resource_by_assignee')) {
                        result.fieldMapping.resourceByAssignee = node.getAttribute('resource_by_assignee');

                        if (node.hasAttribute('assignee_user_id')) {
                            const fieldName = node.getAttribute('assignee_user_id');
                            result.fieldNames.add(fieldName);
                            result.fieldMapping['assignee_user_id'] = fieldName;
                        }
                    }
                }
            }
        });
        return result
    },
});
