/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class FacebookSidebarCategory extends Component {

    /**
     * @returns {FacebookSidebarCategory}
     */
    get facebookcategory() {
        console.log("category facebook",this.props.record);
        return this.props.record;
    }
}

Object.assign(FacebookSidebarCategory, {
    props: { record: Object },
    template: 'mail.FacebookSidebarCategory',
});

registerMessagingComponent(FacebookSidebarCategory);
