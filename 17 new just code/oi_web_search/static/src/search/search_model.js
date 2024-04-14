/** @odoo-module **/
import { SearchModel } from "@web/search/search_model";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { formatDate,formatDateTime,parseDate,parseDateTime  } from "@web/core/l10n/dates";

patch(SearchModel.prototype, {
		
	async load(config) {

        const context = Object.assign({}, config.context);
        
        const searchRangeDefaults = {};

        for (const key in context) {
            const defaultValue = context[key];
            const searchDefaultMatch = /^search_range_default_(.*)$/.exec(key);
            if (searchDefaultMatch) {
                const fieldName = searchDefaultMatch[1];
                searchRangeDefaults[fieldName] = defaultValue;
                delete context[`search_default_${fieldName}`];
                continue;
            }
        }                

        if (Object.keys(searchRangeDefaults).length) {
            config = Object.assign({}, config, {context});
        }            

        await super.load(config);

        for (const [name, values] of Object.entries(searchRangeDefaults)) {
            const field = this.searchViewFields[name];
            if (!field) continue;
            let domainArray, descriptionArray, labels, isDateTime;

            if (field.type ==="date") {
                labels = values.map( value => typeof value ==="string" ? formatDate(parseDate(value)) : value);
                isDateTime = true;
            }
            else if (field.type ==="datetime") {
                labels = values.map( value => typeof value ==="string" ? formatDateTime(parseDateTime(value)) : value);
                isDateTime = true;
            } 
            else {
                labels = values;
                isDateTime = false;
            }
            
            if (values[0] === null) {
                domainArray = [[name, "<=", values[1]]];
                descriptionArray = [field.string, isDateTime ? _t("is before or equal to") : _t("less than or equal to"), labels[1]];
            }
            else if (values[1] === null) {
                domainArray = [[name, ">=", values[0]]];
                descriptionArray = [field.string, isDateTime ? _t("is after or equal to") : _t("greater than or equal to"), labels[0]];
            }
            else {
                domainArray = [[name, ">=", values[0]], [name, "<=", values[1]]];
                descriptionArray = [field.string, _t("is between"), labels[0], _t("and"), labels[1]];
            }            

            const preFilter = {
                description: descriptionArray.join(" "),
                domain: new Domain(domainArray).toString(),
                type: "filter",
            };					            
            this.createNewFilters([preFilter]);				
        }
    }
	
});