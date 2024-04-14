/* @odoo-module */

import { Composer } from "@mail/core/common/composer";
import { Typing } from "@mail/discuss/typing/common/typing";

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useDebounced } from "@web/core/utils/timing";

const commandRegistry = registry.category("discuss.channel_commands");
import { jsonrpc } from "@web/core/network/rpc_service";
import { useService } from "@web/core/utils/hooks";

export const SHORT_TYPING = 5000;
export const LONG_TYPING = 50000;

patch(Composer, {
    components: { ...Composer.components, Typing },
});

patch(Composer.prototype, {

        async _sendMessage(value, postData)  {
            var self = this;
            await super._sendMessage(...arguments);;
            if (!self.connected_with_agent)
            self.getResponseFromBot(value)
        },

        start() {
            this.connected_with_agent = false;
            return super.start();
        },


        setup() {
            this.livechatService = useService("im_livechat.livechat");
            return super.setup();
        },
        scrollToBottom: function () {
            var self = this;
            var $target = $(".o_mail_thread")
            if ($('.odoo-chat-loader:last').length)
            $target.scrollTop($target[0].scrollHeight+$('.odoo-chat-loader:last')[0].scrollHeight);
        },

        getResponseFromBot(message){
            var self = this;
            setTimeout(() => {
                var shadowHost = document.querySelector('.o-livechat-root')
                var shadowRoot = shadowHost.shadowRoot;
                var chatLoaderElements = shadowRoot.querySelectorAll('.odoo-chat-loader');
                if (chatLoaderElements.length > 0) {
                    var lastChatLoaderElement = chatLoaderElements[chatLoaderElements.length - 1];
                    lastChatLoaderElement.classList.remove('d-none');
                  }
            }, 500);
            return jsonrpc('/mail/bot/response', { uuid: this.livechatService.thread.uuid, message_content: message }
            ).then(function (response) {
                if (!response) {
                    try {
                        self.displayNotification({
                            message: _t("Session expired... Please refresh and try again."),
                            sticky: true,
                        });
                    } catch (err) {
                        /**
                         * Failure in displaying notification happens when
                         * notification service doesn't exist, which is the case
                         * in external lib. We don't want notifications in
                         * external lib at the moment because they use bootstrap
                         * toast and we don't want to include boostrap in
                         * external lib.
                         */
                        console.warn(_t("Session expired... Please refresh and try again."));
                    }
                    self._closeChat();
                }
                if (response.connected_with_agent)
                self.connected_with_agent = response.connected_with_agent;
                setTimeout(() => {
                    var shadowHost = document.querySelector('.o-livechat-root')
                    var shadowRoot = shadowHost.shadowRoot;
                    var chatLoaderElements = shadowRoot.querySelectorAll('.odoo-chat-loader');
                    if (chatLoaderElements.length > 0) {
                        chatLoaderElements.forEach(function(element) {
                            element.classList.add('d-none');
                        });
                    }
                }, 500);
                
            });
    },
});




