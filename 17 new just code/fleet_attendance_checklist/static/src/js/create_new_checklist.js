/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { debounce } from "@bus/workers/websocket_worker_utils";
import PublicWidget from "@web/legacy/js/public/public_widget";

export const FleetAttendanceChecklist = PublicWidget.Widget.extend({
    selector: '#wrapwrap:has(.o_fleet_attendance_checklist)',
    events: {
        "click .o_submmit": debounce(function (ev) {
            this._onClickSubmit(ev);
        }, 200, true),

        'change select.o_trip_state': debounce(function (ev) {
            this._onTripStateChanged(ev);
        }, 200, true),

        'change input.o_partner_checked_in': debounce(function (ev) {
            this._onCheckInChanged(ev);
        }, 200, true),

        'change input.o_partner_checked_out': debounce(function (ev) {
            this._onCheckOutChanged(ev);
        }, 200, true),

        'click button.o_check_in_alarm': debounce(function (ev) {
            this._onCheckInAlarm(ev);
        }, 200, true),

        'click button.o_check_out_alarm': debounce(function (ev) {
            this._onCheckOutAlarm(ev);
        }, 200, true),
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
        this.notification = this.bindService("notification");
    },

    _onTripStateChanged: async function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var self = this;
        
        var id = $("input.fleet_attendance_id").val();
        var value = $("#o_trip_state option:selected").val();
        
        if (id != undefined && value != undefined){
            await self.rpc('/fleet_attendance_checklist/on_trip_state_changed', {
                'trip_id': id,
                'trip_state': value,
            });
        }
    },

    _onCheckInChanged: async function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var self = this;

        var newDate = new Date();
        var dateString =
            newDate.getUTCFullYear() + "-" +
            ("0" + (newDate.getUTCMonth()+1)).slice(-2) + "-" +
            ("0" + newDate.getUTCDate()).slice(-2) + " " +
            ("0" + newDate.getUTCHours()).slice(-2) + ":" +
            ("0" + newDate.getUTCMinutes()).slice(-2) + ":" +
            ("0" + newDate.getUTCSeconds()).slice(-2);

        var lineid = $(ev.currentTarget).data('id');
        var is_checked = false;

        if (ev.currentTarget.checked) {
            is_checked = true;
        } else {
            is_checked = false;
        }

        if (lineid != undefined){
            await self.rpc('/fleet_attendance_checklist/on_checkin_changed', {
                'trip_line_id': lineid,
                'checked_in': is_checked,
                'checked_in_time': is_checked ? dateString : '',
            });
        }
    },

    _onCheckOutChanged: async function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var self = this;

        var newDate = new Date();
        var dateString =
            newDate.getUTCFullYear() + "-" +
            ("0" + (newDate.getUTCMonth()+1)).slice(-2) + "-" +
            ("0" + newDate.getUTCDate()).slice(-2) + " " +
            ("0" + newDate.getUTCHours()).slice(-2) + ":" +
            ("0" + newDate.getUTCMinutes()).slice(-2) + ":" +
            ("0" + newDate.getUTCSeconds()).slice(-2);

        var lineid = $(ev.currentTarget).data('id');     
        var is_checked = false;

        if (ev.currentTarget.checked) {
            is_checked = true;
        } else {
            is_checked = false;
        }

        if (lineid != undefined){
            await self.rpc('/fleet_attendance_checklist/on_checkout_changed', {
                'trip_line_id': lineid,
                'checked_out': is_checked,
                'checked_out_time': is_checked ? dateString : '',
            });
        }
    },

    _onClickSubmit: async function(ev){
        ev.stopPropagation();
        ev.preventDefault();
        var self = this;

        var id = $(ev.currentTarget).data('id');

        var result = await self.rpc('/fleet_attendance_checklist/on_submit', {
            'trip_id': id,
            'state': 'completed',
        });

        if (result){
            var web_base_url = window.origin;               
            if (result) {                    
                window.location = web_base_url + '/my/fleet_attendances';
            } else {
                window.location = web_base_url+ '/my/fleet_attendance/error_message'
            }   
        }
    },


    _onCheckInAlarm: async function(ev){
        ev.stopPropagation();
        ev.preventDefault();            
        var self = this;
        
        var lineid = $(ev.currentTarget).data('id');

        if (lineid != undefined){
            var alarm = await self.rpc('/fleet_attendance_checklist/on_checkin_alarm', {
                'trip_line_id': lineid,
                'type': 'check_in',
            });
            if (alarm){
                if(alarm['message'] === 'success'){
                    self.notification.add(
                        _t("Alert message sent successfully."),
                        { type: 'success', sticky: true }
                    );                    
                }else{
                    self.notification.add(
                        _t("Alert message sent unsuccessfully."),
                        { type: 'warning', sticky: true }
                    );
                }
            }
        }
    },

    _onCheckOutAlarm: async function(ev){
        ev.stopPropagation();
        ev.preventDefault();            
        var self = this;
        
        var lineid = $(ev.currentTarget).data('id');

        if (lineid != undefined){
            var alarm = await self.rpc('/fleet_attendance_checklist/on_checkout_alarm', {
                'trip_line_id': lineid,
                'type': 'check_out',
            });
            if (alarm){
                if(alarm['message'] === 'success'){
                    self.notification.add(
                        _t("Alert message sent successfully."),
                        { type: 'success', sticky: true }
                    );                    
                }else{
                    self.notification.add(
                        _t("Alert message sent unsuccessfully."),
                        { type: 'warning', sticky: true }
                    );
                }
            }
        }
    }
});
PublicWidget.registry.FleetAttendanceChecklist = FleetAttendanceChecklist;