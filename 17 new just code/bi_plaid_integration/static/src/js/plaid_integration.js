/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
const { Component, useState } = owl;

export class BiActionButtonFormViewController extends FormController {
    async token_initialize() {
        var bank_id = this.props.context.params.id
        var handler = Plaid.create({
            token: (await $.post('/create_link_token')),
            onLoad: function() {
            },
            onSuccess: function(public_token, metadata) {
                $.post('/exchange_public_token', {
                    public_token: public_token,
                }, function(data){
                    $.post('/create_plaid_account', {
                        bank_id: bank_id
                    });
                });
            },
            onExit: function(err, metadata) {
                if (err != null) {
                }
            },
            onEvent: function(eventName, metadata) {
            }
        });
        handler.open();
    }
}

export const PlaidFormView = {
    ...formView,
    Controller: BiActionButtonFormViewController,
};

registry.category("views").add("bi_plaid_form_view", PlaidFormView);
