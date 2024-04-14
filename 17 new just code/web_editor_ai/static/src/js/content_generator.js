/** @odoo-module **/

import { Component, useState, useRef, onWillStart} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


export class ContentGenerator extends Component {
    static components = { Dialog };
    static template = 'web_editor_ai.content_generator';

    static props = {
        insert: Function,
    };

    setup() {
        this.orm = useService('orm');
        const params = new URLSearchParams(window.location.hash);
        this.previewContainer = useRef('previewContainer')
        this.previewContent = useRef('previewContent')
        this.context = {
            'model': params.get('model'),
            'id': params.get('#id') || params.get('id')
        }

        this.state = useState({});

        onWillStart(async () => {

            const generatorOptions = await this._getOptions();

            this.state.about = generatorOptions['about']
            this.state.length_options = generatorOptions['length']
            this.state.tone_options = generatorOptions['tone']
            this.state.format_options = generatorOptions['format']

            this.state.tone = this.state.tone_options[this.state.tone_options.length - 1][2]
            this.state.format = this.state.format_options[this.state.format_options.length - 1][2]
            this.state.length = this.state.length_options[this.state.length_options.length - 1][2]

        })
    }

    async _confirm() {
        try {
            let text

            if (this.state.previewContent) {
                text = this.state.previewContent;
            } else {
                if (this._checkRequiredFields()) {
                    text = await this._getPreviewContent()
                } else return
            }

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

   async _preview() {
        if (this._checkRequiredFields()) {
            this.state.previewContent = await this._getPreviewContent()

            this.previewContainer.el.classList.remove('d-none');
            this.previewContent.el.innerHTML = this.state.previewContent
        }
    }


    async _getPreviewContent() {
        const final_data = {
            about: this.state.about,
            tone: this.state.tone,
            format: this.state.format,
            length: this.state.length,
        };

        const aiResponse = await this.orm.call("ai.api", 'generate_content', [final_data]);
        return aiResponse
    }

    _checkRequiredFields(){
        if (this.state.about) {
            return true
        } else {
            this.env.services.dialog.add(AlertDialog, {
                body: _t("AI needs to know what to write about!"),
            });
            return false
        }
    }

    async _getOptions() {
        const options = await this.orm.call("content.generator.options", 'get_options', [this.context]);

        return options
    }

}