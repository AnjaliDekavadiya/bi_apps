/* @odoo-module */

import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class LunchFaceRecognitionConfirm extends Component {
    static props = ["*"];
    static template = "lunch_kiosk_mode_adv.LunchRecognitionConfirm";
    setup() {
        this.action = this.props.action;

        this.user = useService("user");
        this.rpc = useService("rpc");
        this.actionService = useService("action");
        this.notificationService = useService('notification');

        this.next_action = 'lunch_kiosk_mode_adv.lunch_action_kiosk_mode';
        this.user_id = this.action.user_id;
        this.user_name = this.action.user_name;

        this.clockRef = useRef("o_lunch_clock");

        this.state = useState({
            clock_start : false,
            _interval : window.setInterval(this._callServer.bind(this), (60 * 60 * 1000 * 24)),
        });

        onMounted(async () => {
            await this.startClock();
            await this.redirectInvalidUser();
        });
    }
    async redirectInvalidUser(){
        var self = this;
        if (!self.user_id){
            await self.rpc("/web/dataset/call_kw/lunch.product/get_lunch_kiosk_mode_action", {
                model: "lunch.product",
                method: "get_lunch_kiosk_mode_action",
                args: [],
                kwargs: {}
            }).then(async function(result) {
                if (result.action) {
                    await self.actionService.doAction(result.action, {clear_breadcrumbs: true});
                }else if (result.warning) {
                    self.notificationService.add(result.warning,{ 
                        type: "danger" 
                    });
                }
            });
        }
    }
    onClickBack(){
        this.actionService.doAction(this.next_action, {clear_breadcrumbs: true}); 
    }
    
    async openLuncKanban(){
        var self = this;
        var context = self.user.context;
        await self.rpc("/web/dataset/call_kw/res.users/order_lunch_recognition", {
            model: "res.users",
            method: "order_lunch_recognition",
            args: [[self.user_id], self.next_action],
            kwargs: {
                context
            },
        }).then(async function(result) {
            if (result.action) {
                await self.actionService.doAction(result.action);
            }else if (result.warning) {
                self.notificationService.add(result.warning,{ 
                    type: "danger" 
                });
            }
        });
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
}

LunchFaceRecognitionConfirm.components = {
    Layout,
}
registry.category("actions").add("lunch_kiosk_mode_adv.lunch_recognition_confirm", LunchFaceRecognitionConfirm);