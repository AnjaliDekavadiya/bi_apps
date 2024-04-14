/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class WhatsappSidebarCategory extends Component {

    /**
     * @returns {WhatsappSidebarCategory}
     */
    setup() {
        this.sidebardropdown = false;
        super.setup();
    }
    
    get watsapcategory() {
        console.log("category=======================",this.props.record);
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

Object.assign(WhatsappSidebarCategory, {
    props: { record: Object },
    template: 'mail.WhatsappSidebarCategory',
});

registerMessagingComponent(WhatsappSidebarCategory);
