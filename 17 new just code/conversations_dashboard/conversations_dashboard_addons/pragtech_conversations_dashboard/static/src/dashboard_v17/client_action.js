/* @odoo-module */

import { attachComponent } from "@web/legacy/utils";
import { loadBundle } from "@web/core/assets";
import Widget from "@web/legacy/js/core/widget";
import publicWidget from '@web/legacy/js/public/public_widget';
import { Whatsapp } from "@pragtech_conversations_dashboard/dashboard_v17/whatsapp_widget";
import { InternalRecords } from "@pragtech_conversations_dashboard/dashboard_v17/internal_records";

import { Component, onWillStart, onWillUpdateProps, onWillUnmount, onWillDestroy, useState } from "@odoo/owl";

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * @typedef {Object} Props
 * @property {Object} action
 * @property {Object} action.context
 * @property {number} [action.context.active_id]
 * @property {Object} [action.params]
 * @property {number} [action.params.active_id]
 * @extends {Component<Props, Env>}
 */
export class WhatsappClientAction extends Component {
    static components = { Whatsapp, InternalRecords };
    static props = ["*"];
    static template = "whatsapp.ClientAction";

    setup() {
        this.store = useState(useService("mail.store"));
        this.messaging = useState(useService("mail.messaging"));
        this.threadService = useService("mail.thread");
        onWillStart(() => this.restoreWhatsappThread(this.props));
        onWillUpdateProps((nextProps) => this.restoreWhatsappThread(nextProps));
        onWillDestroy(() => this.destroy());
    }

    /**
     * Restore the discuss thread according to the active_id in the action
     * if necessary: thread is different than the one already displayed and
     * we are not in a public page. If the thread is not yet known, fetch it.
     *
     * @param {Props} props
     */
    async destroy(){
        console.log("message===",this.messaging);
        // this.messaging.initialize();
        const thread = this.store.Thread.get({ model:"mail.box", id:"inbox" })
        this.threadService.setDiscussThread(thread);
    }
    async restoreWhatsappThread(props) {
        await this.messaging.isReady;
        if (this.store.inPublicPage) {
            return;
        }
        const rawActiveId =
            props.action.context.active_id ??
            props.action.params?.active_id ??
            this.store.Thread.localIdToActiveId(this.store.discuss.thread?.localId) ??
            "mail.box_inbox";
        const activeId =
            typeof rawActiveId === "number" ? `discuss.channel_${rawActiveId}` : rawActiveId;
        let [model, id] = activeId.split("_");
        if (model === "mail.channel") {
            // legacy format (sent in old emails, shared links, ...)
            model = "discuss.channel";
        }
        const activeThread = this.store.Thread.get({ model, id });
        if (!activeThread || activeThread.notEq(this.store.discuss.thread)) {
            // console.log("store discuss", this.store.discuss)
            // console.log("Thread====", this.store.Thread);
            const thread =
                this.store.Thread.get({ model, id }) ??
                (await this.threadService.fetchChannel(parseInt(id)));
            const newthread = Object.values(this.store.Thread.records).filter(
                (thread) => thread.is_pinned && thread.type === "multi_livechat_NAMEs"
                );
            // console.log("threads==", newthread)
            if (!newthread) {
                return;
            }
            if (newthread.length>0){
                if (!newthread[0].is_pinned) {
                    await this.threadService.pin(newthread[0]);
                }
                this.threadService.setDiscussThread(newthread[0]);
            }
        }
    }
}

registry.category("actions").add("all.widgets.conversation", WhatsappClientAction);