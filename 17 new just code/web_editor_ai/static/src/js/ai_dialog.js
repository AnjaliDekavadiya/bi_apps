/** @odoo-module **/

import { Component, useState, useRef, onWillStart} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


export class AiDialog extends Component {
    static components = { Dialog };
    static template = 'web_editor_ai.request_dialog';

    setup() {
        this.orm = useService('orm');
        this.aiRequestInput = useRef('aiRequestInput')

    }

    async _confirm() {
        try {
            let text

            if (this._checkRequiredFields()) {
                text = await this._getContent()
            } else return


            this.props.close();
            this.props.insert(text);
        } catch (e) {
            this.props.close();
            throw e;
        }
    }

    async _cancel() {
        this.props.close();
    }

    async _getContent() {

        const data = this.aiRequestInput.el.value
        const aiResponse = await this.orm.call("ai.api", 'vanilla_request', [data]);
        return aiResponse
    }


    _checkRequiredFields(){
        if (this.aiRequestInput.el.value) {
            return true
        } else {
            this.env.services.dialog.add(AlertDialog, {
                body: _t("AI needs to know what to write about!"),
            });
            return false
        }
    }

}