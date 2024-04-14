/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class WhatsappSidebarCategoryItem extends Component {

    /**
     * @returns {WhatsappSidebarCategoryItem}
     */
    get FacebookcategoryItem() {
        return this.props.record;
    }

}

Object.assign(WhatsappSidebarCategoryItem, {
    props: { record: Object },
    template: 'mail.WhatsappSidebarCategoryItem',
});

export class FacebookSidebarCategoryItem extends Component {

    /**
     * @returns {FacebookSidebarCategoryItem}
     */
    get categoryItem() {
        if (this.props.record.channel.channel_type == 'multi_livechat_NAME'){
            return this.props.record;
        }
    }

}

Object.assign(FacebookSidebarCategoryItem, {
    props: { record: Object },
    template: 'mail.FacebookSidebarCategoryItem',
});

registerMessagingComponent(WhatsappSidebarCategoryItem);
registerMessagingComponent(FacebookSidebarCategoryItem);
