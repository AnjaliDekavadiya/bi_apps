/* @odoo-module */

import { onMounted, onWillUnmount, useRef } from "@odoo/owl";

import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";


patch(FormRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount);
        this.formRootRef = useRef("compiled_view_root");
        this.qr_timer = 0;
        this.orm = useService("orm");
    },
    onMounted() {
        if (this.formRootRef) {
            var self = this;
            const isQRFrom = $(this.formRootRef.el).closest('.o_form_view').hasClass('qr_code_form');
            if (isQRFrom) {
                if (this.env.config.viewArch.className == 'qr_code_form') {
                    $(this.formRootRef.el).closest('.o_form_view').find('.qr_img').attr('src', this.env.searchModel.context.qr_image)
                }
                const resID = this.props.record && this.props.record.evalContext.context && this.props.record.evalContext.context.wiz_id;
                if (resID) {
                    this.qr_timer = setInterval(async function() {
                        try {
                            const res = await self.orm.call('whatsapp.msg', 'get_qr_img', [resID]);
                            if (res) {
                                $(self.formRootRef.el).find('img.qr_img').attr('src', res);
                            }
                        } catch(err) {
                            console.error(err);
                        }
                    }, 9000);
                }
                $(this.formRootRef.el).find('button.send_btn').on('click', function() {
                    clearInterval(self.qr_timer);
                });
                $(this.formRootRef.el).find('button.close_btn').on('click', function() {
                    clearInterval(self.qr_timer);
                });
            }
        }
    },
    onWillUnmount() {
        if (this.formRootRef) {
            const isQRFrom = $(this.formRootRef.el).closest('.o_form_view').hasClass('qr_code_form');
            if (isQRFrom && this.qr_timer) {
                clearInterval(this.qr_timer);
            }
        }
    },
});
