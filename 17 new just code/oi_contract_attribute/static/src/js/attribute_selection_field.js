/** @odoo-module **/

import { Component, tags as owlTags, useRef, onMounted, getParentComponent  } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { useService } from "@web/core/utils/hooks";
import { useGetDefaultLeafDomain } from "@web/core/domain_selector/utils";
import { useLoadFieldInfo } from "@web/core/model_field_selector/utils";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class FieldCharAttributeSelection extends CharField {
    static props = {
        ...standardFieldProps,
    };
    setup() {
		
        this.root = useRef("root");
		super.setup(...arguments);

        onMounted(() => {
            const value = this.props.record.data[this.props.name];
            console.log('test')
            console.log(value)
            if (value && this.root.el) {
				
				const el = this.root.el;
	            const search = () => {
	                const source = parent.attribute_selection_values || [];
	                el.autocomplete("option", "source", source);
	                if (source) {
	                    try {
	                        el.autocomplete("search", "");
	                    } catch (err) {}
	                }
	            };
	
	            const search2 = () => {
	                const source = parent.attribute_selection_values || [];
	                el.autocomplete("option", "source", source);
	                if (source && el.value === "") {
	                    try {
	                        $el.autocomplete("search", "");
	                    } catch (err) {}
	                }
	            };
	
	            el.autocomplete({
	                source: values,
	                minLength: 0,
	                select: function (event, ui) {
	                    self._setValue(ui.item.value);
	                },
	            }).on("click", search2).on("dblclick", search);
					
			}

            
        });

       
    }
}


export const attributeSelection = {
    ...CharField,
    component: FieldCharAttributeSelection,
};

registry.category("fields").add("attribute_selection", attributeSelection);


/*export class FieldCharAttributeSelection2 extends CharField{
	setup() {
        
        var def = this._super.apply(this, arguments);
        var self = this;
        if (this.record.data.has_selection) {        	
        	var get_selection;
        	if (self.record.data.attribute_id.selection_values) {
        		get_selection = $.Deferred();
        		get_selection.resolve(self.record.data.attribute_id.selection_values);
        	} else {
        		get_selection = this._rpc({
            		model : 'hr.attribute',
            		method : 'get_selection',
            		args : [this.record.data.attribute_id.res_id, false],
            		context : session.user_context        		
            	});
        	}        	
        	get_selection.then(function(values){        		
        		self.record.data.attribute_id.selection_values = values;
        		
        		var search = function(){
        			 try {
        				 $(this).autocomplete("search", '');
        			 } catch(err)  {}
        		};
        		
        		var search2 = function(){
        			if ($(this).val() == "")
        				try {
           				 	$(this).autocomplete("search", '');
           			 	} catch(err) { }
        		};
        		        		
        		self.$el.autocomplete({
        			source : values,
        			minLength: 0,
        			select : function (event, ui ) {
        				self._setValue(ui.item.value);
        			}
        		}).click(search2).dblclick(search);
        	}) ;
        }
        else {
        	if (self.$el.hasClass('ui-autocomplete-input')) {
        		self.$el.autocomplete("destroy");
            	self.$el.removeData('autocomplete');
        	}        	
        }
        return def;
        
        }}


export const attributeSelection2 = {
    ...CharField,
    component: FieldCharAttributeSelection2,
};

registry.category("fields").add("attribute_selection2", attributeSelection2);*/
