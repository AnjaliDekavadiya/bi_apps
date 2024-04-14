/** @odoo-module */

import { registry } from "@web/core/registry";
import {CharField} from "@web/views/fields/char/char_field";

const { Component } = owl;

export class AppraisalEvaluationPage extends Component {
	static template = 'oi_appraisal.AppraisalEvaluationPage';
	
	get group() {
		return this.props.group;
	}

	get has_lines() {
		return this.props.evaluation.has_lines;
	}
	
	onChange(group, line, value) {		
		return this.props.evaluation.onChange(group, line, value);
	}
		
	makeTooltip(line) {
		const info = {
			text: line.description
		}
		return JSON.stringify(info);
	}	
	
	getFieldComponent(line) {
		return registry.category("fields").get(line.widget, CharField);
	}

	getFieldProps(group, line) {
		const self = this;
		const field_name = `_evaluation_${line.id}`;
		const field_type = {
			radio: "selection"
		}[line.widget] || line.widget;
		const required = !line.optional;
		const props = {
			name: field_name,
			readonly: self.props.readonly,
			record: {
				isRequired : () => required,
				isInvalid : () => false,
				fields : {
					[field_name] : {
						selection : line.selection,
						type: field_type,
						string: field_name,
					}
				},
				data: {
					[field_name] : line.value
				},
				model: {
					bus: {
						trigger: () => {

						},
						addEventListener: () => {

						},
						removeEventListener: () => {

						}
					}
				},
				isFieldInvalid: () => false,
				update: (changes) => {
					self.onChange(group,line, changes[field_name]);
				}
			}			
		};
		
		props.record.activeFields = props.record.fields;
		
		if (line.widget =='float') {
			props.value = parseFloat(props.value);
		}
		
		return props;
	}	
}
