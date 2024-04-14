/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { insert } from '@mail/model/model_field_command';

const ODOO_CHANNEL_GROUPS = [
    "channel_channel",
    "channel_direct_message",
    "channel_private_group",
    "channel_livechat",
];

registerPatch({
    name: 'MessagingInitializer',
    recordMethods: {
        async _init(data) {
            await this._super(data);
            // TODO: find a better way
            // console.log(data.channels);
            console.log("=======data.multi_livechat==========",data.multi_livechat);
            this.messaging.multi_livechat = data.multi_livechat;
            // await this.async(() => this._initChannels(data.multi_livechat));
        },
        async _initChannels(channelsData) {
            await this._super(channelsData);
            console.log("initializing facebook channels", channelsData)
            let channel_list = [];
            for (const key in channelsData) {
                const startsWith = key.lastIndexOf("multi_livechat_") === 0;
                if (startsWith && !(key in ODOO_CHANNEL_GROUPS)) {
                    channel_list = channel_list.concat(channelsData[key]);
                }
            }
            // TODO: multi_livechat_types: channel_type -> Channel Name
            console.log("channel list are", channel_list)
            return this.messaging.executeGracefully(
                channel_list.map((data) => () => {
                    const channel = this.messaging.models["Thread"].insert(
                        this.messaging.models["Thread"].convertData(data)
                    );
                    if (!channel.isPinned) {
                        channel.pin();
                    }
                })
            );
        },
    }
});

