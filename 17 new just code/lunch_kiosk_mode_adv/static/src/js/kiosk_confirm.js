/* @odoo-module */

import { Component, onWillStart, onMounted, useRef, onWillDestroy, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { browser } from "@web/core/browser/browser";
import { useService } from "@web/core/utils/hooks";

export class LunchKioskConfirm extends Component {
    static props = ["*"];
    static template = "lunch_kiosk_mode_adv.LunchKioskConfirm";
    setup() {
        this.action = this.props.action;
        this.rpc = useService("rpc");
        this.orm = useService('orm');
        this.actionService = useService("action");
        this.notification = useService('notification');

        this.clockRef = useRef("o_lunch_clock");

        this.padButtons = [
            ...Array.from({ length: 9 }, (_, i) => [i + 1]), // [[1], ..., [9]]
            ["C", "btn-warning"],
            [0],
            ["OK", "btn-primary"],
        ];

        this.lockPad = false;
        this.next_action = 'lunch_kiosk_mode_adv.lunch_action_kiosk_mode';
        this.user_id = this.action.user_id || false;
        this.user_name = this.action.user_name || false;

        this.state = useState({
            codePin: "",
            clock_start : false,
            _interval : window.setInterval(this._callServer.bind(this), (60 * 60 * 1000 * 24)),
        });

        const onKeyDown = async (ev) => {
            const allowedKeys = [...Array(10).keys()].reduce((acc, value) => { // { from '0': '0' ... to '9': '9' }
                acc[value] = value;
                return acc;
            }, 
            {
                'Delete': 'C',
                'Enter': 'OK',
                'Backspace': null,
            });
            const key = ev.key;

            if (!Object.keys(allowedKeys).includes(key)) {
                return;
            }

            ev.preventDefault();
            ev.stopPropagation();

            if (allowedKeys[key]) {
                await this.onClickPadButton(allowedKeys[key]);
            }
            else {
                this.state.codePin = this.state.codePin.substring(0, this.state.codePin.length - 1);
            }
        }

        onMounted(() => {
            this.startClock();
        });

        onWillUnmount(() => {
            clearInterval(this.state.clock_start);
            clearInterval(this.state._interval);
        });

        browser.addEventListener('keydown', onKeyDown);
        onWillStart(() => browser.addEventListener('keydown', onKeyDown))
        onWillDestroy(() => browser.removeEventListener('keydown', onKeyDown));
    }

    startClock() {
        var self = this;
        console.log(this.clockRef.el)
        self.state.clock_start = setInterval(function () {            
            $(self.clockRef.el).text(new Date().toLocaleTimeString(navigator.language, {
                hour: '2-digit', minute: '2-digit', second: '2-digit'
            }));
        }, 500);
        // First clock refresh before interval to avoid delay
        $(self.clockRef.el).show().text(new Date().toLocaleTimeString(navigator.language, { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    }
    _callServer() {
        // Make a call to the database to avoid the auto close of the session
        return this.rpc("/lunch_kiosk_mode_adv/lunch_kiosk_keepalive", {});
    }

    async onClickPadButton(value) {
        if (this.lockPad) {
            return;
        }
        if (value === "C") {
            this.state.codePin = "";
        } else if (value === "OK") {
            this.lockPad = true;
            await this.onClickOkButton()            
            this.state.codePin = "";
            this.lockPad = false;
        }
        else {
            this.state.codePin += value;
        }
    }
    async onClickOkButton(){
        var self = this;
        let result = await this.orm.call('res.users','order_lunch_manual',[[this.user_id], this.next_action, this.state.codePin])
        if (result && result.action) {
            self.actionService.doAction(result.action);
        } 
        else if (result && result.warning) {
            self.notification.add(result.warning, {
                type: 'danger',
            });
            self.state.codePin = "";
            self.lockPad = false;
        }
    }
    onClickBack(){
        console.log(this.next_action)
        this.actionService.doAction(this.next_action, {clear_breadcrumbs: true}); 
    }
}
LunchKioskConfirm.components = {
    Layout,
}
registry.category("actions").add("lunch_kiosk_mode_adv.lunch_kiosk_confirm", LunchKioskConfirm);