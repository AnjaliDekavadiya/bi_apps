/* @odoo-module */

import { useService } from "@web/core/utils/hooks";

import { Component, useState } from "@odoo/owl";

/**
 * @typedef {Object} Props
 * @property {import("models").Thread} thread
 * @property {string} size
 * @property {string} className
 * @extends {Component<Props, Env>}
 */
export class WhatsappThreadIcon extends Component {
    static template = "whatsapp.ThreadIcon";
    static props = ["thread", "size?", "className?"];
    static defaultProps = {
        size: "medium",
        className: "",
    };

    setup() {
        this.store = useState(useService("mail.store"));
        console.log('chat partner====', this.props.thread.chatPartner)
        console.log('chat thread====', this.props.thread);       
    }

    get chatPartner() {
        console.log('chat partner====', this.props.thread.chatPartner)
        console.log('chat thread====', this.props.thread);
        return this.props.thread.chatPartner;
    }
}
