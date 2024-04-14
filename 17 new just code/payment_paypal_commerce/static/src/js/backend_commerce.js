/** @odoo-module **/
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";
import { renderToElement } from "@web/core/utils/render";

export class SellerOnboarding extends Component {

    async setup() {
        var self = this;
        return await jsonrpc(
                "/paypal_commerce/authorize/json",
                {}
            ).then(function (result){
                self.status = result.status
                self.error_msg = result.error_msg
                self.auth_status = result.auth_status
                self.email_status = result.email_status
                self.url = result.url;
                var content = renderToElement("SellerOnboardingMenu", {widget: self});
                $(".o_content").replaceWith(content);
            });
            
    }

};
SellerOnboarding.template = "SellerOnboardingMenu";
SellerOnboarding.props = {
    record: { type: Object, optional: true},
};;
registry.category("actions").add("paypal_commerce_setup_action2", SellerOnboarding);
