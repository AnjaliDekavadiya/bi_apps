/* @odoo-module */

import { Record } from "@mail/core/common/record";
import { Messaging } from "@mail/core/common/messaging_service";

import { patch } from "@web/core/utils/patch";

patch(Messaging.prototype, {
    initMessagingCallback(data) {
        super.initMessagingCallback(data);
        this.store.multi_livechat = data.multi_livechat;
        this.store.messages_status = data.messages;
        let channel_list = [];
        for (const key in data.channels) {
            const startsWith = data.channels[key].channel_type.lastIndexOf("multi_livechat_") === 0;
            if (startsWith) {
                channel_list = channel_list.concat(data.channels[key]);
            }
        }
        console.log("channel list are", channel_list)
        // return this.messaging.executeGracefully(
        channel_list.map((data) => {
            // console.log("mapppppppppppp",data)
            const channel = this.store.Thread.insert(
                {
                    ...data,
                    model: "discuss.channel",
                    type: data.channel_type,
                }
            );
            if (data.channel_type === "multi_livechat_NAMEs"){
                this.store.discuss.multi_livechat.threads.add(channel);
            }
            // const channel = this.store.Thread.insert(
            //     this.store.Thread.convertData(data)
            // );
            if (!channel.isPinned) {
                // channel.pin();
                // this.threadService.pin(channel);
                this.env.services["mail.thread"].pin(channel);
            }
        });
        console.log("this.store.discuss =======", this.store)
        // );
        console.log("messaging_service ===", data)
        console.log("this_data ===", this)
    },
});