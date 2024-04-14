/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";

export class NotificationPopUp extends AbstractAwaitablePopup {
    static template = "NotificationPopUp";
    static defaultProps = {
        title: "Confirm ?",
        body: "",
    };

    setup() {
        super.setup();
    }
  }
