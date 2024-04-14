/** @odoo-module **/

import { Component,toRaw } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { Record } from "@web/model/record";
import { Field } from "@web/views/fields/field";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { useGetDefaultLeafDomain } from "@web/core/domain_selector/utils";
import { formatDate,formatDateTime,serializeDate,serializeDateTime } from "@web/core/l10n/dates";
import { useLoadFieldInfo } from "@web/core/model_field_selector/utils";

export class SearchMenu extends Component {
    static template = "oi_web_search.SearchMenu";
    static components = {
        Dropdown, DropdownItem, Record, Field
    }
    static props = {
        slots: { type: Object, optional: true }
    };

    async setup() {
        this.orm = useService("orm");
        this.fieldService = useService("field");
        this.dialogService = useService("dialog");
        this.loadFieldInfo = useLoadFieldInfo(this.fieldService)
        this.getDefaultLeafDomain = useGetDefaultLeafDomain();
        this.searchItems = [];
        this.fields = {};
        this.values = {};
        this.initialValues = {};
        
        for await (const item of this.getSearchItems()) {
            if (item.fieldName in this.fields) continue;
            this.searchItems.push(item);
            this.fields[item.fieldName] = item.field;
            this.initialValues[item.fieldName] = item.field.type == "many2many" ? [] : false;
            if (item.fieldName2) {
                this.fields[item.fieldName2] = item.field;
                this.initialValues[item.fieldName2] = false;
            }
        }	        
        this.activeFields = this.fields;
    }

    get isDebugMode() {
        return !!this.env.debug;
    }

    get resModel() {
        return this.env.searchModel.resModel;
    }

    getFieldWidget(field) {
        if (field.type == "many2many")
            return "search_menu.many2many_tags";

        if (field.type == "selection")
            return "selection_tags";

        return field.type;
    }

    async *getSearchItems() {
        for (const searchItem of Object.values(this.env.searchModel.searchItems)) {
            if (searchItem.type !== "field") continue;            
            const field = Object.assign({}, this.env.searchModel.searchViewFields[searchItem.fieldName], {
                translate: false
            });                        
            if (field.type === "one2many") {
                let ignore = true;
                if (searchItem.filterDomain) {
                    const domain = new Domain(searchItem.filterDomain);
                    if (domain.ast.type === 4 && domain.ast.value.length === 1 && domain.ast.value[0].type === 10) {
                        const [domainFields, domainOprator, domainValue] = domain.ast.value[0].value;                        
                        if (domainFields.type === 1 && domainValue.type === 5 && domainValue.value =="self") {
                            const {fieldDef} = await this.loadFieldInfo(this.resModel, domainFields.value);
                            if (fieldDef) {
                                ["type","relation", "domain", "digits"].forEach(name => field[name] = fieldDef[name]);
                                ignore = false;
                            }                            
                        }
                    }                    
                }
                if (ignore) continue;
            }

            if (field.type == "many2one")
                field.type = "many2many";

            const fieldProps = {
                name: field.name,
                type: this.getFieldWidget(field)
            }
            if (field.type == "selection") {
                fieldProps.selection_model = this.resModel;
                fieldProps.selection_field = field.name;
            }

            const item = {
                ...searchItem,
                field,
                fieldProps,
                range: ['date', 'datetime', 'float', 'integer', 'monetary'].includes(field.type)
            }            
            if (item.range) {
                item.fieldName2 = '_to_' + item.fieldName;
                item.fieldProps2 = {
                    ...item.fieldProps,
                    name: item.fieldName2
                }                
            }
            yield item;		
        }	    
    }

    get recordProps() {        
        const { resModel, fields, activeFields, initialValues } = this;
        const onRecordChanged = this.onRecordChanged.bind(this);
        const props = {
            resModel, fields, activeFields, values: initialValues, onRecordChanged
        };
        return props;
    }

    onRecordChanged(record, changes) {
        for(const [name, value] of Object.entries(record.data)) {
            const field = this.fields[name];
            if (field.type == "many2many") 
                this.values[name] = toRaw(value.currentIds);                       
            else 
                this.values[name] = toRaw(value);
        }
    }

    makeTooltip(searchItem) {
        const info = {
            debug: Boolean(odoo.debug),
            field: {
                ...searchItem,
                label: searchItem.description,
                name: searchItem.field.name,
                help: searchItem.field.help,
                type: searchItem.fieldType,
                domain: searchItem.field.domain,
                relation: searchItem.field.relation,
                selection: searchItem.field.selection,
            },
        };
        return JSON.stringify(info);	
    }

    async _getMany2manyAutoCompletionValues(item, ids) {
        const records = await this.orm.read(item.field.relation, ids, ["display_name"]);
        return records.map(record => {
            return {
                label : record.display_name,
                value: record.id,
                operator: item.operator || '='
            }            
        });
    }

    async _getSelectionAutoCompletionValues(item, values) {
        const fieldAttributes = await this.fieldService.loadFields(this.resModel, {fieldNames: [item.fieldName], attributes : ["selection"]});
        const selection = fieldAttributes[item.fieldName].selection;
        return values.map(value => {
            return {
                label : selection.find(s => s[0] == value)[1],
                value,
                operator: item.operator || '='
            }            
        });
    }

    _getValue(fieldName) {
        const value = this.values[fieldName];
        if (value === undefined) return false;
        return value;
    }
    
    async _applySearchItem(item) {
        const value = this._getValue(item.fieldName);
        if (value === "" || value === false || value === undefined) return;
        if (Array.isArray(value) && value.length === 0) return;

        const field = this.fields[item.fieldName];
        let values;

        if (field.type == "many2many")
            values = await this._getMany2manyAutoCompletionValues(item,value);

        else if (field.type == "selection")
            values = await this._getSelectionAutoCompletionValues(item,value);

        else values = [{
            label: value,
            value: value,
            operator: item.operator || 'ilike'
        }];

        values.forEach(autocompleteValue => this.env.searchModel.addAutoCompletionValues(item.id, autocompleteValue));                
    }

    async _applySearchItemRange(item) {
        const value1 = this._getValue(item.fieldName);
        const value2 = this._getValue(item.fieldName2);        
        
        if (value1 === false && value2 === false)
            return;
        
        let domainArray, descriptionArray;

        function getValue(value) {
            if (item.field.type == "date")
                return serializeDate(value);
            if (item.field.type == "datetime")
                return serializeDateTime(value);
            return value;
        }

        function getLabel(value) {
            if (item.field.type == "date")
                return formatDate(value);
            if (item.field.type == "datetime")
                return formatDateTime(value);
            return value;
        }

        if (value1 !==false && value2 === false) {
            domainArray = [[item.fieldName, ">=", getValue(value1)]];
            descriptionArray = [item.description, _t("greater than or equal to"), getLabel(value1)];
        }
        else if (value1 ===false && value2 !== false) {
            domainArray = [[item.fieldName, "<=", getValue(value2)]];
            descriptionArray = [item.description, _t("less than or equal to"), getLabel(value2)];
        }
        else {
            domainArray = [[item.fieldName, ">=", getValue(value1)], [item.fieldName, "<=", getValue(value2)]];
            descriptionArray = [item.description, _t("is between"), getLabel(value1), _t("and"), getLabel(value2)];
        }
        const preFilter = {
            description: descriptionArray.join(" "),
            domain: new Domain(domainArray).toString(),
            type: "filter",
        };					
        
        this.env.searchModel.createNewFilters([preFilter]);				
    }

    async _onApplyButtonClick() {
        this.searchItems.forEach(item => {
            if (item.range) {
                this._applySearchItemRange(item);
            }
            else {
                this._applySearchItem(item);
            }
        });
    }

    async _onAdvanceButtonClick() {
        const { domainEvalContext: context, resModel } = this.env.searchModel;
        const domain = await this.getDefaultLeafDomain(resModel);
        this.dialogService.add(DomainSelectorDialog, {
            resModel,
            defaultConnector: "|",
            domain,
            context,
            onConfirm: (domain) => this.env.searchModel.splitAndAddDomain(domain),
            disableConfirmButton: (domain) => domain === `[]`,
            title: _t("Add Custom Filter"),
            confirmButtonText: _t("Add"),
            discardButtonText: _t("Cancel"),
            isDebugMode: this.env.searchModel.isDebugMode,
        });
    }
}

