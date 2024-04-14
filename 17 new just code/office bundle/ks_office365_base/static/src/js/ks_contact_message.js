/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { Component} from "@odoo/owl";
import {registry} from "@web/core/registry";

export class BaseContactMessage extends Component {
    KsContactMessage(parent, action) {
        var self = parent;
        if (action.params.task == "warn") {
            self.do_warn(
                _t("Error"),
                _t(action.params.message)
            );
        }
    }
}
BaseContactMessage.template = 'ks_base_contact_message';
registry.category("actions").add("ks_contact_message_id", BaseContactMessage);