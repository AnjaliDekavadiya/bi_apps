/** @odoo-module **/

import { ContentDialog } from './content_dialog';
import { onMounted, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc_service";

export class ContentPromptDialog extends ContentDialog {
    static template = 'wk_chatgpt_engine.ContentPromptDialog';
    static props = {
        ...super.props,
        initialPrompt: { type: String, optional: true },
        id: { type: Number, optional: true },
        model: { type: String, optional: true },
        dialog : { type: String, optional: true },

    };
    static defaultProps = {
        initialPrompt: '',
    };

    async setup() {
        super.setup();
        this.orm = useService("orm");
        onWillStart(async () => {
            this.prompt = await this.getPrompt();
            this.tone = await this.getTone();
            this.content_length = await this.getContentLength();
            this.odooApiKey = await this.getOdooApiKey();
            this.conversationHistory = [{
                role: 'system',
                content: 'You are a helpful assistant with the aim of professionally generating content for the user.',
            },
            {
                role: 'assistant',
                content: 'What can I assist you with?',
            }];
        });

        $(document).on('change','.promptTone',this.onchangeTone.bind(this))

        
        onMounted(() => {
            var $self = this;
            $(self.promptInput).val($self.prompt)
            $(self.promptLength).val($self.content_length)
            const tonesHtml = $self.tone.map(element => `
            <div class="form-check">
                <input class="promptTone form-check-input" type="radio" name="promptTone"  id="${element.id}"/>
                <label class="form-check-label" for="${element.id}" >
                ${element.name}
                </label>
            </div>
            `);
            $(self.promptTone).html(tonesHtml)
          });

        this.promptInputRef = useRef('promptInput');


    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    async onchangeTone(ev) {
        var $self = this;
        const tone_id = parseInt($(ev.currentTarget).attr('id'))

        $self.changeTone = await jsonrpc('/web/dataset/call_kw/ai.content.wizard/change_tone', {
            model: 'ai.content.wizard',
            method: 'change_tone',
            args: [],
            kwargs: { id: $self.props.id, model: $self.props.model, tone:tone_id}
        });
        $(self.promptInput).val($self.changeTone)
        $self.prompt = $self.changeTone
    }

    getOdooApiKey(){
        return this.orm.call("ai.content.wizard", "get_odooapi_key")
    }

    getContentLength(){
        return this.orm.call("ai.content.wizard", "get_content_length", [], {id: this.props.id, model:this.props.model})
    }

    getPrompt(){
        return this.orm.call("ai.content.wizard", "get_prompt", [], {id: this.props.id, model:this.props.model})
    }


    getTone(){
        return this.orm.call("ai.content.wizard", "get_tone", [], {id: this.props.id, model:this.props.model})
    }


    change_tone(){
        return this.orm.call("ai.content.wizard", "change_tone", [], {id: this.props.id, model:this.props.model, })
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
