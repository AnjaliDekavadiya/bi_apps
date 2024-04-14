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
                    if (node.hasAttribute('resource_type')) {
                        result.fieldMapping.resourceType = node.getAttribute('resource_type');
                    }
                    if (!!result.fieldMapping.resourceType && node.hasAttribute('fc_premium_license')) {
                        result.fieldMapping.schedulerLicenseKey = node.getAttribute('fc_premium_license');
                    }
                    if (result.fieldMapping.resourceType === 'timegrid') {
                        result.scales = ['day', 'week'];
                    } else if (!!result.fieldMapping.resourceType) {
                        result.scales = ['day', 'week', 'month'];
                    }
                }
            }
        });
        return result
    },
});
