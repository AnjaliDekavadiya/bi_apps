/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
import { assignIn } from "@mail/utils/common/misc";
import { assignDefined } from "@mail/utils/common/misc";
import { url } from "@web/core/utils/urls";
import { patch } from "@web/core/utils/patch";

patch(Thread, {
    _insert(data) {
        const thread = super._insert(...arguments);
        if (thread.type === "multi_livechat_NAMEs") {
            assignIn(thread, data, ["anonymous_name", "anonymous_country"]);
            // console.log("adding whatsapp thread", this.store.discuss)
            this.store.discuss.multi_livechat.threads.add(thread);
            this.env.services["mail.thread"].sortChannels();
        }
        if (thread.type === "multi_livechat_NAME") {
            assignIn(thread, data, ["anonymous_name", "anonymous_country"]);
            this.store.discuss.facebook_livechat.threads.add(thread);
            this.env.services["mail.thread"].sortChannels();
        }
        if (thread.type === "multi_livechat_NAME2") {
            assignIn(thread, data, ["anonymous_name", "anonymous_country"]);
            this.store.discuss.instagram_livechat.threads.add(thread);
            this.env.services["mail.thread"].sortChannels();
        }
        return thread;
    },
});

patch(Thread.prototype, {
    update(data) {
        super.update(data);
        console.log("Update data===", data)
        const { id, name, attachments, description, ...serverData } = data;
        if (serverData) {
            // if ("channel" in data) {}
            if ("channelMembers" in data) {
                if (this.type === "multi_livechat_NAMEs") {
                    for (const member of this.channelMembers) {
                        if (
                            member.persona.notEq(this._store.user) ||
                            (this.channelMembers.length === 1 &&
                                member.persona?.eq(this._store.user))
                        ) {
                            this.chatPartner = member.persona;
                        }
                    }
                }
                if (this.type === "multi_livechat_NAME" || this.type === "multi_livechat_NAME2") {
                    for (const member of this.channelMembers) {
                        if (
                            member.persona.notEq(this._store.user) ||
                            (this.channelMembers.length === 1 &&
                                member.persona?.eq(this._store.user))
                        ) {
                            this.chatPartner = member.persona;
                        }
                    }
                }
            }
        }
    },

    get hasMemberList() {
        return this.type === "multi_livechat_NAMEs" || super.hasMemberList;
    },

    get correspondents() {
        return super.correspondents.filter((correspondent) => !correspondent.is_bot);
    },

    get correspondent() {
        let correspondent = super.correspondent;
        if (this.type === "multi_livechat_NAMEs" && !correspondent) {
            // For livechat threads, the correspondent is the first
            // channel member that is not the operator.
            const orderedChannelMembers = [...this.channelMembers].sort((a, b) => a.id - b.id);
            const isFirstMemberOperator = orderedChannelMembers[0]?.persona.eq(this.operator);
            correspondent = isFirstMemberOperator
                ? orderedChannelMembers[1]?.persona
                : orderedChannelMembers[0]?.persona;
        }
        return correspondent;
    },

    get imgUrl() {
        if (!this.type in ["multi_livechat_NAMEs", "multi_livechat_NAME", "multi_livechat_NAME2"]) {
            return super.imgUrl;
        }
        if (this.chatPartner){
        const partner_id = this.chatPartner.id;
        return url(
            `/web/image/res.partner/${partner_id}/avatar_128`
        );
        }
    
    },

    // /**
    //  *
    //  * @param {import("models").Persona} persona
    //  */
    // getMemberName(persona) {
    //     if (this.type !== "livechat") {
    //         return super.getMemberName(persona);
    //     }
    //     if (persona.user_livechat_username) {
    //         return persona.user_livechat_username;
    //     }
    //     return super.getMemberName(persona);
    // },
});
