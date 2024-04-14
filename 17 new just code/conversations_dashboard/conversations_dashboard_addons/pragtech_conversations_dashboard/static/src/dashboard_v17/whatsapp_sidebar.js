/* @odoo-module */

import { Component, useState } from "@odoo/owl";

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export const discussSidebarItemsRegistry = registry.category("whatsapp.discuss_sidebar_items");

/**
 * @typedef {Object} Props
 * @extends {Component<Props, Env>}
 */
export class WhatsappSidebar extends Component {
    static template = "mail.WhatsappSidebar";
    static props = {};
    static components = {};

    setup() {
        this.store = useState(useService("mail.store"));
        this.messaging = useState(useService("mail.messaging"));
        this.action = useService("action");
        this.threadService = useState(useService("mail.thread"));
    }

    get discussSidebarItems() {
        return discussSidebarItemsRegistry.getAll();
    }

    _onClickChannelAdd(ev) {
        ev.stopPropagation();
        let action = {
            res_model: 'whatsapp.msg.send.partner',
            name: _t('Send a WhatsApp Message'),
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'new',
        };
        this.action.doAction(action);
        // this.action.doAction(action, {
        //     onClose: () => this.env.bus.trigger('lunch_update_dashboard')
        // });
    }

    async _onClickRefresh(ev) {
        ev.stopPropagation();
        var self = this;
        // const discuss_new = self.discussView
        // console.log("===active id==", discuss_new);
        console.log("===this sidebar===", this);
        // this.messaging.initializer.restartWhatsapp(this.MultiLivechatGroups[0].chats);
        console.log("after start", this.store.discuss.multi_livechat);
        console.log("discussSidebarItems======", this.discussSidebarItems);
        await this.messaging.initialize();
        if (this.store.discuss.thread){
            await this.threadService.fetchNewMessages(this.store.discuss.thread);
            await this.threadService.fetchMoreAttachments(this.store.discuss.thread);
        }
        await this.threadService.sortChannels();
        // await this.MultiLivechatGroups[0].chats.onClick();
    }
}
