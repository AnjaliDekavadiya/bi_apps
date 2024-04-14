/** @odoo-module */

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Notebook } from "@web/core/notebook/notebook";
import { AppraisalEvaluationPage } from "../evaluation_page/evaluation_page";

import { Component } from "@odoo/owl";

export class AppraisalEvaluation extends Component {
	static template = 'oi_appraisal.AppraisalEvaluation';
	static props = {
		...standardFieldProps,
	};
	static components = {
		Notebook
	};

    setup() {
                
	}	    			
	
    onChange(group, line, value) {		
        const data = JSON.parse(JSON.stringify(this.data));        
        data.groups.filter(g => g.id == group.id)[0].lines.filter(l => l.id == line.id)[0].value = value;
        this.props.record.update({ [this.props.name]: data }, { save: this.props.autosave });
    }		

    get data() {
        return this.props.record.data[this.props.name] || {}
    }
    	
	
	get pages() {
		const self = this;
		return this.data.groups.map(function(group){
			return {
				Component: AppraisalEvaluationPage,
				title: group.name,
				props: {
					group: group,
					evaluation: self,
					readonly: self.props.readonly
				}
			}
		});
	}
}

export const appraisalEvaluation = {
    component: AppraisalEvaluation,
    supportedTypes: ["json"],
};


registry.category("fields").add('appraisal_evaluation', appraisalEvaluation);