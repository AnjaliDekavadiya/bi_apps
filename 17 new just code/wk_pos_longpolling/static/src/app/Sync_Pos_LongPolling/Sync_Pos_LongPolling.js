/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { NotificationPopUp } from "@wk_pos_longpolling/app/notifications/popups/notification_popup";

export class SyncPosLongPolling extends Component {
    static template = "wk_pos_longpolling.SyncPosLongPolling";

    setup() {
        this.pos = usePos();
    }

    async mounted() {
        var self = this;
        await super.mounted();
        // changed the sync status of pos longpolling
        $(".pos_longpolling_status").addClass("active");
        $(".pos_longpolling_status .fa-refresh").removeClass("fa-spin");
        $(".pos_longpolling_status .fa-refresh").css({
            color: "rgb(94, 185, 55)",
        });
        console.log("############ websocket response received #########)");
    }

    /**
   * This method check if the current tab is the master tab at the bus level.
   * We have to close all other tabs on the same hostname to connect pos longpolling faster.
   *
   */
    sync_pos_longpolling() {
        var self = this;
        if ($('.pos_longpolling_status').length && $('.pos_longpolling_status').hasClass('from_pos_model')) {
            self.pos.showScreen("PartnerListScreen");
            self.pos.showScreen("ProductScreen");
            $('.pos_longpolling_status').removeClass('from_pos_model');
        } else if ($('.pos_longpolling_status').length && !$('.pos_longpolling_status').hasClass('active')) {
            self.pos.startpolling();
            self.pos.popup.add(NotificationPopUp, {
                title: _t("Information !!!!"),
                body: _t("Close all other tabs on the same hostname to connect POS Websocket faster.")
            });
        } else
            self.pos.popup.add(NotificationPopUp, {
                title: _t("Information !!!!"),
                body: _t("POS Websocket is already connected.")
            });
    }
}

