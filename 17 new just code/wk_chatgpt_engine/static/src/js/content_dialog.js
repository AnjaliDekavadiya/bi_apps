/** @odoo-module **/

import { Component, useState, markup, onWillDestroy, status } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { escape } from "@web/core/utils/strings";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";


export class ContentDialog extends Component {
    
    static components = { Dialog };
    static props = {
        close: Function,
        insert: Function,
    };

    setup() {
        this.rpc = useService('rpc');
        this.state = useState({ selectedMessageId: null });
        onWillDestroy(() => this.pendingRpcPromise?.abort());
    }


    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------


    _postprocessGeneratedContent(content) {
        const lines = content.split('\n').filter(line => line.trim().length);
        const fragment = document.createDocumentFragment();
        let parentUl, parentOl;
        let lineIndex = 0;
        for (const line of lines) {
            if (line.trim().startsWith('- ')) {
                parentUl = parentUl || document.createElement('ul');
                const li = document.createElement('li');
                li.innerText = line.trim().slice(2);
                parentUl.appendChild(li);
            } else if (
                (parentOl && line.startsWith(`${parentOl.children.length + 1}. `)) ||
                (!parentOl && line.startsWith('1. ') && lines[lineIndex + 1]?.startsWith('2. '))
            ) {
                parentOl = parentOl || document.createElement('ol');
                const li = document.createElement('li');
                li.innerText = line.slice(line.indexOf('.') + 2);
                parentOl.appendChild(li);
            } else {
                [parentUl, parentOl].forEach(list => list && fragment.appendChild(list));
                parentUl = parentOl = undefined;
                const block = document.createElement(line.startsWith('Title: ') ? 'h2' : 'p');
                block.innerText = line;
                fragment.appendChild(block);
            }
            lineIndex += 1;
        }
        [parentUl, parentOl].forEach(list => list && fragment.appendChild(list));
        return fragment;
    }


    _cancel() {
        this.props.close();
    }

    _confirm() {
        try {
            this.env.services.ui.block();
            this.props.close();
            const text = this.state.messages.text;
            this.props.insert(this._postprocessGeneratedContent(text || ''));
            this.env.services.ui.unblock();
        } catch (e) {
            this.props.close();
            throw e;
        }
    }
    
    _generate_content(prompt, callback) {
        const protectedCallback = (...args) => {
            if (status(this) !== 'destroyed') {
                delete this.pendingRpcPromise;
                return callback(...args);
            }
        }
        this.pendingRpcPromise = this.rpc('/web_editor/generate_text', {
            prompt,
            conversation_history: this.conversationHistory,
        }, { shadow: true });
        return this.pendingRpcPromise
            .then(content => protectedCallback(content))
            .catch(error => protectedCallback(_t(error.data?.message || error.message), true));
    }


    _generate_content_openai(prompt, callback) {
        const protectedCallback = (...args) => {
            if (status(this) !== 'destroyed') {
                delete this.pendingRpcPromise;
                return callback(...args);
            }
        }
        this.pendingRpcPromise = this.rpc('/web/dataset/call_kw/ai.content.wizard/process_ai_content', {
            model: 'ai.content.wizard',
            method: 'process_ai_content',
            args: [],
            kwargs: {model:this.props.model, prompt : prompt, toneLength : parseInt($('#promptLength').val())}
        });
        return this.pendingRpcPromise
        .then(content => protectedCallback(content))
        .catch(error => protectedCallback(_t(error.data?.message || error.message), true));
    }

    _grammar_correction_openai(prompt, callback) {
        const protectedCallback = (...args) => {
            if (status(this) !== 'destroyed') {
                delete this.pendingRpcPromise;
                return callback(...args);
            }
        }
        this.pendingRpcPromise = this.rpc('/web/dataset/call_kw/ai.grammar.wizard/process_grammar_content', {
            model: 'ai.grammar.wizard',
            method: 'process_grammar_content',
            args: [],
            kwargs: { prompt : prompt, lang : this.props.currentLang, model:this.props.model}
        });
        return this.pendingRpcPromise
        .then(content => protectedCallback(content))
        .catch(error => protectedCallback(_t(error.data?.message || error.message), true));
    }


    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    async insertMessage() {
        if (this.state.messages) {
            this._confirm();
        } else {
            this.previewPrompt().then(() => {
                this._confirm();
            });
        }
    }


    formatContent(content) {
        return markup([...this._postprocessGeneratedContent(content).childNodes].map(child => {
            const nodes = new Set([...child.querySelectorAll('*')].flatMap(node => node.childNodes));
            nodes.forEach(node => {
                if (node.nodeType === Node.TEXT_NODE) {
                    node.textContent = escape(node.textContent);
                }
            });
            return child.outerHTML;
        }).join(''));
    }

    previewPrompt() {
        this.env.services.ui.block();
        const prompt = this.prompt && this.prompt.trim() ? this.prompt.trim() : this.state.prompt;
        const conversation = { role: 'user', content: prompt };
        this.conversationHistory.push(conversation);
        if (this.odooApiKey){
            return this._generate_content(prompt, (content, isError) => {
                if (isError) {
                    this.conversationHistory = this.conversationHistory.filter(c => c !== conversation);
                } else {
                    this.conversationHistory.push({ role: 'assistant', content });
                }
                this.state.messages = {
                    author: 'assistant',
                    text: content,
                    isError,
                };
                $(self.promptContent).removeClass("d-none")
                $(self.promptContent).val(this.state.messages.text)
                $(self.grammarCorrected).removeClass("d-none")
                $(self.grammarCorrected).val(this.state.messages.text)
                this.env.services.ui.unblock();
            });
        }else if (this.props.dialog === 'prompt'){
            return this._generate_content_openai(prompt, (content, isError) => {
                if (isError) {
                    this.conversationHistory = this.conversationHistory.filter(c => c !== conversation);
                } else {
                    this.conversationHistory.push({ role: 'assistant', content });
                }
                this.state.messages = {
                    author: 'assistant',
                    text: content,
                    isError,
                };
                $(self.promptContent).removeClass("d-none")
                $(self.promptContent).val(this.state.messages.text)
                this.env.services.ui.unblock();
            });
        }else{
            return this._grammar_correction_openai(prompt, (content, isError) => {
                if (isError) {
                    this.conversationHistory = this.conversationHistory.filter(c => c !== conversation);
                } else {
                    this.conversationHistory.push({ role: 'assistant', content });
                }
                this.state.messages = {
                    author: 'assistant',
                    text: content,
                    isError,
                };
                $(self.grammarCorrected).removeClass("d-none")
                $(self.grammarCorrected).val(this.state.messages.text)
                this.env.services.ui.unblock();
            });
        }
    }




}
