/* @odoo-module */

// import { ChatbotStep } from "@im_livechat/embed/common/chatbot/chatbot_step_model";

import { Message } from "@mail/core/common/message_model";

import { patch } from "@web/core/utils/patch";

patch(Message.prototype, {

    get messageSeen() {
        // if (!this.author || !this._store.self) {
        //     return false;
        // }
        // return this.author.eq(this._store.self);
        console.log("message this====", this);
        if (!this._store.messages_status) {
            return;
        }
        
        const def = this._store.messages_status.find((message) => message.id === this.id);
        console.log("compute def==", def);
        if (def){
            return def.message_seen;
        }
        return false;
        
    }
});
