/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { _t } from "@web/core/l10n/translation";

export class ManaRecordSelector extends Component {

    static template = "mana_dashboard.record_selector";
    static components = {
        MultiRecordSelector
    };

    static props = {
        resIds: { type: Array, element: Number },
        resModel: String,
        update: Function,
        domain: { type: Array, optional: true },
        context: { type: Object, optional: true },
        fieldString: { type: String, optional: true },
        placeholder: { type: String, optional: true },
    };

    static defaultProps = {
        context: {},
        domain: [],
    };

    setup() {
        super.setup();
        this.state = useState({
            resIds: this.props.resIds,
        });
    }

    update(resIds) {
        debugger
        this.state.resIds = resIds;
        this.props.update(resIds);
    }
};
