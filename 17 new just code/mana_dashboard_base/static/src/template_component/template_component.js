/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, xml } from "@odoo/owl";

export class TemplateWidget extends Component {
    get isReadonly() {
        return true;
    }
}


TemplateWidget.props = {
    ...standardFieldProps,
    template:  {
        type: String,
        optional: true,
    }
};

TemplateWidget.template = xml`
<div>
    <t t-call="{{this.props.template}}" />
</div>`

export const templateWidget = {
    component: TemplateWidget,
    displayName: _t("Template Widget"),
    supportedTypes: ["char"],
    extractProps: ({ attrs, options }) => ({
        template: options.template
    }),
};

registry.category("fields").add("template_widget", templateWidget);
