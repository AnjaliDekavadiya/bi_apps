/** @odoo-module **/

import { ContentDialog } from './content_dialog';
import { onMounted, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class grammarCorrectionDialog extends ContentDialog {
    static template = 'wk_chatgpt_engine.grammarCorrectionDialog';
    static props = {
        ...super.props,
        initialPrompt: { type: String, optional: true },
        id: { type: Number, optional: true },
        model: { type: String, optional: true },
        innerText : { type: String, optional: true },
        dialog : { type: String, optional: true },
        currentLang : { type: String, optional: true },
    };
    static defaultProps = {
        initialPrompt: '',
    };

    async setup() {
        super.setup();
        this.orm = useService("orm");
        this.prompt = this.props.textContent || this.props.innerText;
        onWillStart(async () => {
            this.odooApiKey = await this.getOdooApiKey();
            this.conversationHistory = [{
                role: 'system',
                content: `You will be provided with statements, and your task is to convert them to ${this.props.currentLang}.`,
            },
            {
                role: 'assistant',
                content: 'What can I assist you with?',
            }];
        });
        
        onMounted(() => {
            var $self = this;
            $(self.grammarContent).val($self.prompt)
          });

        this.promptInputRef = useRef('promptInput');


    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------


    getOdooApiKey(){
        return this.orm.call("ai.content.wizard", "get_odooapi_key")
    }


    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _cancel() {
        super._cancel();
    }
    /**
     * @override
     */
     _confirm() {
        super._confirm();
    }
}
