/** @odoo-module **/

import { Many2ManyTagsField, many2ManyTagsFieldColorEditable } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { registry } from "@web/core/registry";

export class SearchMenuMany2ManyTagsField extends Many2ManyTagsField {

    static defaultProps = {
        ...Many2ManyTagsField.defaultProps,
        canCreate: false,
        canQuickCreate: false,
        canCreateEdit: false,
    };

    setup() {
        super.setup();
        this._update = this.update;
        this._names = {};
        this.update = async (recordlist) => {            
            if (recordlist.some(r => r.display_name === undefined)) {
                const ids = recordlist.map(record => record.id);
                recordlist = await this.orm.read(this.relation, ids, ["display_name"]);
            }

            recordlist.forEach(record => {
                this._names[record.id] = record.display_name;
            });

            this._update(recordlist);
        }
    }

    getTagProps(record) {
        const res = super.getTagProps(record);
        res.text = this._names[record.resId];
        return res;
    }
}

export const searchMenuMany2ManyTagsField = {
    ...many2ManyTagsFieldColorEditable,
    component: SearchMenuMany2ManyTagsField
}

registry.category("fields").add("search_menu.many2many_tags", searchMenuMany2ManyTagsField);

