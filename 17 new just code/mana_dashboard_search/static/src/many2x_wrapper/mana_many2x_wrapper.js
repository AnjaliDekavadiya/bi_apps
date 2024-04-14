/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { _t } from "@web/core/l10n/translation";

export class ManaX2manyWrapper extends Component {

    static template = "mana_dashboard.x2many_wrapper";
    static components = {
        Many2XAutocomplete
    };

    static props = {
        resModel: String,
        context: {
            type: Object,
            optional: true,
        },
        domain: {
            type: Array,
            optional: true,
        },
        value: {
            type: Object,
            optional: true,
        },
        onSelect: {
            type: Function,
            optional: true,
        },
        isToMany: {
            type: Boolean,
            optional: true,
        }
    };

    static defaultProps = {
        context: {},
        domain: [],
        value: {},
        onSelect: () => { },
        isToMany: false,
    };

    setup() {
        super.setup();
        this.state = useState({
            field: this.props.value,
        });
    }

    getDomain() {
        return this.props.domain || [];
    }

    onSelect(selection) {
        if (this.props.isToMany) {
            if (selection) {
                this.state.field = selection;
            } else {
                this.state.field = []
            }
        } else {
            if (selection) {
                this.state.field = selection[0];
            } else {
                this.state.field = {};
            }
        }
        this.props.onSelect(selection);
    }
};
