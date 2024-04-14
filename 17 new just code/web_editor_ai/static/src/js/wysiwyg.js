/** @odoo-module **/

import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";
import { _t } from "@web/core/l10n/translation";
import * as OdooEditorLib from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
const preserveCursor = OdooEditorLib.preserveCursor;
import  {AiDialog} from '@web_editor_ai/js/ai_dialog';
import  {ContentGenerator} from '@web_editor_ai/js/content_generator';
const parseHTML = OdooEditorLib.parseHTML;
const closestElement = OdooEditorLib.closestElement;
import { useService } from "@web/core/utils/hooks";

import { patch } from "@web/core/utils/patch";
import { markup } from "@odoo/owl";


patch(Wysiwyg.prototype, {
  _getPowerboxOptions() {
        const options = super._getPowerboxOptions();
        const {commands, categories} = options;
        categories.push({name: _t('OpenAI'), priority: 50});
        commands.push(
            {
                category: _t('OpenAI'),
                name: _t('Content Generator'),
                priority: 10,
                description: _t('Let AI to quickly generate content for you.'),
                fontawesome: 'fa-magic',
                callback: async () => this._openContentGenerator('generate_content'),
            },
            {
                category: _t('OpenAI'),
                name: _t('Grammar correction'),
                priority: 10,
                description: _t('Fix mistakes in the selected text.'),
                fontawesome: 'fa-pencil',
                callback: async () => {
                    const selection = this.odooEditor.document.getSelection().toString();
                    if (selection !== undefined && selection.trim() !== '' ) {
                        const response = await this._makeAiRequest(selection, 'correct_text')
                        this.odooEditor.execCommand('insert', response)
                    }
                },
            },
            {
                category: _t('OpenAI'),
                name: _t('Translation'),
                priority: 10,
                description: _t('Translate the selected text.'),
                fontawesome: 'fa-language',
                callback: async () => {
                    const selection = this.odooEditor.document.getSelection().toString();
                    if (selection !== undefined && selection.trim() !== '' ) {
                        const response = await this._makeAiRequest(selection, 'translate_text')
                        this.odooEditor.execCommand('insert', response)
                    }
                },
            },
            {
                category: _t('OpenAI'),
                name: _t('Vanilla Promt'),
                priority: 10,
                description: _t('Ask AI anything.'),
                fontawesome: 'fa-question',
                callback: () => this._openAiRequestBox(),
            },


        );
        return {...options, commands, categories};
    },

    /**
     * Insert the response from OpenAI request
     */
    _openAiRequestBox: function () {
        const restoreSelection = preserveCursor(this.odooEditor.document);

        this.env.services.dialog.add(AiDialog,
            {
            insert: content => {
                this.odooEditor.historyPauseSteps();
                this.odooEditor.execCommand('insert', parseHTML(this.odooEditor.document, content));
                this.odooEditor.historyUnpauseSteps();
                }
            },
           {onClose: restoreSelection})


    },

    /**
     * Insert the response from OpenAI request
     */
    _openContentGenerator: function () {
        const restoreSelection = preserveCursor(this.odooEditor.document);
        this.odooEditor.document.getSelection().collapseToEnd();

       this.env.services.dialog.add(ContentGenerator, {
            insert: content => {
                this.odooEditor.historyPauseSteps();
                this.odooEditor.execCommand('insert', parseHTML(this.odooEditor.document, content));
                this.odooEditor.historyUnpauseSteps();
                }
            },
           {onClose: restoreSelection})
    },

    /**
     * Call the orm method to make the request to OpenAI API
     * @param input
     */
    _makeAiRequest: async function (input, method) {

        const aiResponse = await this.orm.call("ai.api", method, [input]);
        return aiResponse
    }
});

