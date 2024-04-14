/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";

export class QRCodePopup extends AbstractAwaitablePopup {
    static template = "QRCodePopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        confirmKey: "Enter",
        title: _t('Scan QR Code'),
        body: "",
        cancelKey: true,
    };

    setup() {
        super.setup();
        this.state = useState({ message: '', confirmButtonIsShown: false });
    }
}
