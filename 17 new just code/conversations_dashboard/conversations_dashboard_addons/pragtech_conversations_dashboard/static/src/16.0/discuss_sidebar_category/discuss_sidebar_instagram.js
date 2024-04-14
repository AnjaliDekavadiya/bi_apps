/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class InstagramSidebarCategory extends Component {

    /**
     * @returns {InstagramSidebarCategory}
     */
    setup() {
        this.sidebardropdown = false;
        super.setup();
    }
    
    get instagramcategory() {
        // console.log("category",this.props.record);
        return this.props.record;
    }

    async _onclickCategory(ev){
        // ev.stopPropagtion();
        console.log("dropdown clicked")
        if (this.sidebardropdown === true) {
            this.sidebardropdown = false;
        } else {
            this.sidebardropdown = true;
        }
        console.log("=========this.sidebardropdown=========",this.sidebardropdown)
    }
}

Object.assign(InstagramSidebarCategory, {
    props: { record: Object },
    template: 'mail.InstagramSidebarCategory',
});

registerMessagingComponent(InstagramSidebarCategory);