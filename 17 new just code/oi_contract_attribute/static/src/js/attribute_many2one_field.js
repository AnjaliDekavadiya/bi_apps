/** @odoo-module */

import { Component, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
//import { session } from "@web/core/session";

export class FieldMany2OneAttribute extends Many2OneField {
    async _update_selection_values() {
        //const parent = this.env.getParent();
        this.attribute_selection_values = false;
        console.log(this.props.record.data.attribute_id.res_id)
        if (this.props.record.data.attribute_id.res_id) { 
            const result = await this.rpc({
                model: 'hr.attribute',
                method: 'get_selection',
                args: [this.props.record.data.attribute_id.res_id, false],
                context: session.user_context
            });
            //console.log(result)
            this.attribute_selection_values = result;
        }
    }
    
    setup() {
        super.setup();
        const self = this;

        onMounted(async () => {
            await self._update_selection_values();
           //console.log(self.attribute_selection_values)
        });
        
        
    }
}

export const attributeMany2one = {
    ...many2OneField,
    component: FieldMany2OneAttribute,
};

registry.category("fields").add("attribute_many2one", attributeMany2one);
