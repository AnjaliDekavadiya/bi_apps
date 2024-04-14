/* @odoo-module */

import { Component, onWillStart, onMounted, useRef, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { url } from "@web/core/utils/urls";
import { LunchRecognitionDialog } from "./lunch_recognition_dialog"
import { _t } from "@web/core/l10n/translation";

export class LunchKioskMode extends Component {
    static props = ["*"];
    static template = "lunch_kiosk_mode_adv.LunchKioskMode";

    setup() {
        this.rpc = useService("rpc");
        this.orm = useService('orm');
        this.user = useService("user");
        this.dialog = useService("dialog");
        this.actionService = useService("action");
        this.notification = useService('notification');

        this.clockRef = useRef("o_lunch_clock");

        this.state = useState({
            company_name: false,
            company_image_url: false,
            lunch_face_recognition: false,
            clock_start : false,
            _interval : window.setInterval(this._callServer.bind(this), (60 * 60 * 1000 * 24)),
            faceClassName: 'd-none',
        });

        this.labeledFaceDescriptors = [];

        onWillStart(async () => {
            const company_id = session.user_companies.allowed_companies[0] || session.user_companies.current_company || false;
            let company = await this.orm.call('res.company','search_read',[[['id', '=', company_id]], ['name','lunch_face_recognition']])
            if (company){
                this.state.company_name = company[0].name;
                this.state.lunch_face_recognition= company[0].lunch_face_recognition,
                this.state.company_image_url = url("/web/image", {
                    model: "res.company",
                    id: company[0].id,
                    field: "logo",
                });
            }
        });

        onMounted(async () => {
            await this.startClock();
            await this.initRecognition();
        });


        onWillUnmount(() => {
            clearInterval(this.state.clock_start);
            clearInterval(this.state._interval);
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

    onManuallySelect(){
        this.actionService.doAction('lunch_kiosk_mode_adv.res_users_lunch_action_kanban', {
            additional_context: { 'no_group_by': true },
        });
    }

    async initRecognition(){
        var self = this;
        if (window.location.protocol == 'https:') {
            if (self.state.lunch_face_recognition) {
                if (!("Human" in window)) {
                    self._loadHuman();
                } 
                else {
                    await self._loadModels();
                }
            }
        }
    }

    _loadHuman () {
        var self = this;
        if (!("Human" in window)) {
            (function (w, d, s, g, js, fjs) {
                g = w.Human || (w.Human = {});
                g.Human = { q: [], ready: function (cb) { this.q.push(cb); } };
                js = d.createElement(s); fjs = d.getElementsByTagName(s)[0];
                js.src = window.origin + '/lunch_kiosk_mode_adv/static/src/js/lib/source/human.js';
                fjs.parentNode.insertBefore(js, fjs); js.onload = async function () {
                    console.log("apis loaded");
                    await self._loadModels();
                    self.def_face_recognition.resolve();
                };
            }(window, document, 'script'));
        }
    }

    async _loadModels() {
        var self = this;
        const promises = [];
        this.humanConfig = {
            debug: false,
            backend: 'webgl',
            async: true,
            warmup: 'none', //none, face
            cacheSensitivity: 0,
            deallocate: true,
            modelBasePath: '/lunch_kiosk_mode_adv/static/src/lib/models/',
            filter: { enabled: true, equalization: false, flip: false },
            face: { 
                enabled: true, 
                detector: { 
                    rotation: false,
                    minConfidence: 0.6,
                    maxDetected: 1,
                    mask: false,
                    skipInitial: true,
                }, 
                mesh: { 
                    enabled: true 
                }, 
                attention: { 
                    enabled: false 
                }, 
                iris: { 
                    enabled: true 
                }, 
                description: { 
                    enabled: true 
                }, 
                emotion: { 
                    enabled: true 
                }, 
                antispoof: { 
                    enabled: true 
                }, 
                liveness: { 
                    enabled: true 
                } 
            },
            body: { 
                enabled: false 
            },
            hand: { 
                enabled: false 
            },
            object: { 
                enabled: false 
            },
            segmentation: { 
                enabled: false 
            },
            gesture: { 
                enabled: true 
            },
        };
        this.human = new Human.Human(this.humanConfig);
        this.human.env['perfadd'] = false; // is performance data showing instant or total values
        this.human.draw.options.font = 'small-caps 18px "Lato"'; // set font used to draw labels when using draw methods
        this.human.draw.options.lineHeight = 20;
        this.human.validate(this.humanConfig);
        await this.human.load();
        if (true) {
            const warmup = new ImageData(50, 50);
            await this.human.detect(warmup);
        }
        promises.push([this.human]);
        return Promise.all(promises).then(() => {            
            return Promise.resolve().then(async function(){
                await self.loadLabeledImages();
            });
        });
    }

    async loadLabeledImages(){
        var self = this;
        return await this.rpc('/lunch_kiosk_mode_adv/loadLabeledImages/').then(async function (data) {
            data.map((data, i) => {
                const descriptors = [];
                for (var i = 0; i < data.descriptors.length; i++) {
                    if (data.descriptors[i]) {
                        var buffer = self.base64ToArrayBuffer(data.descriptors[i]);
                        self.labeledFaceDescriptors.push({
                            'name': data.name,
                            'label': data.label,
                            'descriptors': Array.from(buffer),
                        });
                    }
                }
            });
            self.state.faceClassName = 'all';
        });
    }

    base64ToArrayBuffer(base64) {
        var self = this;
        var binary_string = window.atob(base64);
        var len = binary_string.length;
        var bytes = new Uint8Array(len);
        for (var i = 0; i < len; i++) {
            bytes[i] = binary_string.charCodeAt(i);
        }
        return new Float32Array(bytes.buffer);
    }
    openFaceRecognition(){
        var self = this;
        if (self.labeledFaceDescriptors && self.labeledFaceDescriptors.length != 0) {
            self.dialog.add(LunchRecognitionDialog, {
                human: self.human,
                labeledFaceDescriptors : self.labeledFaceDescriptors,
                updateRecognitionLunch: (rdata) => this.updateRecognitionLunch(rdata),
            });
        } else {
            self.notification.add(_t("Detection Failed: Resource not found, Please add it to your users profile."), {
                type: 'danger',
            });
        }
    }

    async updateRecognitionLunch({ rdata }) {
        var self = this;
        console.log(rdata);
        if (rdata.user_id, rdata.user_name) {
            self.actionService.doAction({
                type: "ir.actions.client",
                tag: "lunch_kiosk_mode_adv.lunch_recognition_confirm",
                name: _t("Confirm"),
                context: self.user.context,
                user_id: rdata.user_id,
                user_name: rdata.user_name,
                kiosk_mode: true,
            });
        }
    }
}
LunchKioskMode.components = {
    Layout,
}
registry.category("actions").add("lunch_kiosk_mode_adv.lunch_kiosk_mode", LunchKioskMode);