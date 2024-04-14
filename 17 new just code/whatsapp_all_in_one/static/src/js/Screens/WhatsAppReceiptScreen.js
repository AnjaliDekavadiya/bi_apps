/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { QRCodePopup } from "@whatsapp_all_in_one/js/Screens/popup";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";


patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.popup = useService("popup");
    },
    async sendToWhatsApp() {
        var order = this.pos.get_order();
        var self = this;
        var customer = order.partner;
        if (!customer) {
            this.showPopup('ErrorPopup', {
                title: _t('No customer'),
                body: _t('Customer is not selected! Please selected customer to send order receipt.'),
            });
            return;
        }
        if (customer && !customer.mobile) {
            this.showPopup('ErrorPopup', {
                title: _t('No mobile number'),
                body: _t('Can not send WhatsApp message. Mobile number is not available for this customer.'),
            });
            return;
        }
        if (!order) {
            this.showPopup('ErrorPopup', {
                title: _t('No Orer'),
                body: _t('No order available in the system.'),
            });
        }

        var receiptData = document.querySelector(".pos-receipt");
        if (receiptData) {
            receiptData = receiptData.outerHTML || {};
        }
        // const ticketImage = await this.renderer.toJpeg(
        //             OrderReceipt,
        //             {
        //                 data: this.pos.get_order().export_for_printing(),
        //                 formatCurrency: this.env.utils.formatCurrency,
        //             },
        //             { addClass: "pos-receipt-print" }
        //         );
        var is_send_invoice = order.is_to_invoice();
        var message = '';
        if (is_send_invoice) {
            message = _t('Dear *' + customer.name + '*,\nHere is your Invoice for the *' + order.name + '*');
        } else {
            message = _t('Dear *' + customer.name + '*,\nHere is your electronic ticket for the *' + order.name + '*');
        }
        var newContext = {
            'receipt_data': receiptData,
            'active_model': 'pos.order',
            'active_id': order.name,
        };
        var context = Object.assign({}, session.user_context || {}, newContext);
        const msgCreate = {
            'partner_ids': [customer.id],
            'message': message,
        };
        this.ui.block();
        const msgID = await this.orm.create("whatsapp.msg", [msgCreate],{ context: context });
        if (msgID) {
            try {
                const res = await this.orm.call("whatsapp.msg", "action_send_msg", [msgID],{ context: {'from_pos': true} });
                this.ui.unblock();
                var type = is_send_invoice ? "Invoice" : "Receipt";
                if (res && res.name && res.name === 'Scan WhatsApp QR Code') {
                    await this.popup.add(QRCodePopup,  { qr_img: res.qr_img , rec_id: msgID, type: type });
                    return false;
                } else if (res === true) {
                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: _t('Message Sent'),
                        body: _t('Message sent to customer.'),
                    });
                    if (confirmed) {
                        return true;
                    }
                } else {
                    this.popup.add(ErrorPopup, {
                        title: _t('Error sending message'),
                        body: _t('Something went wrong while sending ' + type + ' to WhatsApp.'),
                    });
                }
            } catch (err) {
                this.ui.unblock();
                this.popup.add(ErrorPopup, {
                    title: _t('Error sending message'),
                    body: _t('Something went wrong while sending to WhatsApp.'),
                });
            }
        }
    }
});
