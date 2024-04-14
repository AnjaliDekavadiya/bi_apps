/** @odoo-module **/

import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import "@web_editor/js/wysiwyg/wysiwyg_iframe";
import { useService } from "@web/core/utils/hooks";
import * as OdooEditorLib from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
import { ContentPromptDialog } from './content_prompt_dialog';
import { grammarCorrectionDialog } from './grammar_correction_dialog';
import { session } from "@web/session";

const OdooEditor = OdooEditorLib.OdooEditor;
const preserveCursor = OdooEditorLib.preserveCursor;
const closestBlock = OdooEditorLib.closestBlock;
const closestElement = OdooEditorLib.closestElement;



patch(Wysiwyg.prototype, {


        setup() {
            this.action = useService("action");
            super.setup();

        },

        openContentPromptDialog(mode = 'prompt') {
            const restore = preserveCursor(this.odooEditor.document);
            const params = {
                id : this.options.recordInfo.res_id || 0,
                model : this.options.recordInfo.res_model || '',
                dialog : 'prompt',
                insert: content => {
                    this.odooEditor.historyPauseSteps();

                    while (!this.$root[0].closest('#wrapwrap') && $(this.odooEditor._computeHistorySelection()['focusNode']).parent().text() !== '') {
                    $(this.odooEditor._computeHistorySelection()['focusNode']).parent().text('');
                    }
                    if (this.$root[0].closest('#wrapwrap')){
                        $(this.odooEditor._computeHistorySelection().anchorNode).parent().text('')
                    }
                    const insertedNodes = this.odooEditor.execCommand('insert', content);
                    this.odooEditor.historyUnpauseSteps();
                    this.notification.add(_t('Congratulations! The generated content has been successfully saved.'), {
                        title: _t('Generated content'),
                        type: 'success',
                    });
                    this.odooEditor.historyStep();
                    const start = insertedNodes?.length && closestElement(insertedNodes[0]);
                    const end = insertedNodes?.length && closestElement(insertedNodes[insertedNodes.length - 1]);
                    if (start && end) {
                        const divContainer = this.odooEditor.editable.parentElement;
                        let [parent, left, top] = [start.offsetParent, start.offsetLeft, start.offsetTop - start.scrollTop];
                        while (parent && !parent.contains(divContainer)) {
                            left += parent.offsetLeft;
                            top += parent.offsetTop - parent.scrollTop;
                            parent = parent.offsetParent;
                        }
                        let [endParent, endTop] = [end.offsetParent, end.offsetTop - end.scrollTop];
                        while (endParent && !endParent.contains(divContainer)) {
                            endTop += endParent.offsetTop - endParent.scrollTop;
                            endParent = endParent.offsetParent;
                        }
                        const div = document.createElement('div');
                        div.classList.add('o-chatgpt-content');
                        const FRAME_PADDING = 3;
                        div.style.left = `${left - FRAME_PADDING}px`;
                        div.style.top = `${top - FRAME_PADDING}px`;
                        div.style.width = `${Math.max(start.offsetWidth, end.offsetWidth) + (FRAME_PADDING * 2)}px`;
                        div.style.height = `${endTop + end.offsetHeight - top + (FRAME_PADDING * 2)}px`;
                        divContainer.prepend(div);
                        setTimeout(() => div.remove(), 2000);
                    }
                },
            };

            this.odooEditor.document.getSelection().collapseToEnd();
            this.env.services.dialog.add(
                mode === 'prompt' ? ContentPromptDialog : ContentPromptDialog ,
                params,
                { onClose: restore},
            );
        },

        openGrammarCorrectionDialog(mode = 'grammar') {
            const restore = preserveCursor(this.odooEditor.document);
            const params = {
                id : this.options.recordInfo.res_id || 0,
                model : this.options.recordInfo.res_model || '',
                innerText : this.$el[0].innerText,
                currentLang : this.env.model.config.context.lang,
                dialog : 'grammar',
                insert: content => {
                    this.odooEditor.historyPauseSteps();

                    while (!this.$root[0].closest('#wrapwrap') && $(this.odooEditor._computeHistorySelection()['focusNode']).parent().text() !== '') {
                    $(this.odooEditor._computeHistorySelection()['focusNode']).parent().text('');
                    }
                    if (this.$root[0].closest('#wrapwrap')){
                        $(this.odooEditor._computeHistorySelection().anchorNode).parent().text('')
                    }
                    const insertedNodes = this.odooEditor.execCommand('insert', content);
                    this.odooEditor.historyUnpauseSteps();
                    this.notification.add(_t('Congratulations! The grammar correction has been saved successfully.'), {
                        title: _t('Grammar Correction'),
                        type: 'success',
                    });
                    this.odooEditor.historyStep();
                    const start = insertedNodes?.length && closestElement(insertedNodes[0]);
                    const end = insertedNodes?.length && closestElement(insertedNodes[insertedNodes.length - 1]);
                    if (start && end) {
                        const divContainer = this.odooEditor.editable.parentElement;
                        let [parent, left, top] = [start.offsetParent, start.offsetLeft, start.offsetTop - start.scrollTop];
                        while (parent && !parent.contains(divContainer)) {
                            left += parent.offsetLeft;
                            top += parent.offsetTop - parent.scrollTop;
                            parent = parent.offsetParent;
                        }
                        let [endParent, endTop] = [end.offsetParent, end.offsetTop - end.scrollTop];
                        while (endParent && !endParent.contains(divContainer)) {
                            endTop += endParent.offsetTop - endParent.scrollTop;
                            endParent = endParent.offsetParent;
                        }
                        const div = document.createElement('div');
                        div.classList.add('o-chatgpt-content');
                        const FRAME_PADDING = 3;
                        div.style.left = `${left - FRAME_PADDING}px`;
                        div.style.top = `${top - FRAME_PADDING}px`;
                        div.style.width = `${Math.max(start.offsetWidth, end.offsetWidth) + (FRAME_PADDING * 2)}px`;
                        div.style.height = `${endTop + end.offsetHeight - top + (FRAME_PADDING * 2)}px`;
                        divContainer.prepend(div);
                        setTimeout(() => div.remove(), 2000);
                    }
                },
            };

            this.odooEditor.document.getSelection().collapseToEnd();
            this.env.services.dialog.add(
                mode === 'grammar' ? grammarCorrectionDialog : grammarCorrectionDialog ,
                params,
                { onClose: restore},
            );
        },


        /**
        * @override
        */
        _getPowerboxOptions(ev) {
            const options = super._getPowerboxOptions();
            var self = this;
            options.categories.push({
                name: _t('OpenAI'),
                priority: 300,
            });

            options.commands.push({
                name: _t('Generate Content'),
                category: _t('OpenAI'),
                description: _t("Enable AI to generate the content."),
                fontawesome: 'fa-magic',
                priority: 1,
                isDisabled: () => !this.odooEditor.isSelectionInBlockRoot(),
                callback: async () => this.openContentPromptDialog(),
            });


            options.commands.push({
                name: _t('Grammar Correction'),
                category: _t('OpenAI'),
                description: _t("Correct the mistake in the text."),
                fontawesome: 'fa-edit',
                priority: 1,
                isDisabled: () => !this.odooEditor.isSelectionInBlockRoot(),
                callback: async () => this.openGrammarCorrectionDialog(),
            });


            options.commands.push({
                name: _t('Translate'),
                category: _t('OpenAI'),
                description: _t("Translate the selected text."),
                fontawesome: 'fa-language',
                priority: 1,

                callback: () => {
                    $('.o_form_button_save').click()
                    this.action.doAction({
                        type: 'ir.actions.act_window',
                        name: 'AI Translate Wizard',
                        res_model: 'ai.translate.wizard',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            'active_model_id': this.options.recordInfo.res_id,
                            'active_model_name': this.options.recordInfo.res_model,
                            'active_field': this.$el.offsetParent().attr('name'),
                            'active_content' : this.$el[0].innerText
                        },
                        loadTranslations() {
                            result =  this.orm.call(this.options.recordInfo.res_model, "get_field_translations", [
                                [this.options.recordInfo.res_id],
                                this.$el.offsetParent().attr('name'),
                            ]);
                            console.log("result", result)
                            return result 
                        }

                    });


                },
            });
            return {...options};
        }

    });

