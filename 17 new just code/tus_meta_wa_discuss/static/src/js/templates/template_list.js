/* @odoo-module */
import { ActionPanel } from "@mail/discuss/core/common/action_panel";

import { Dialog } from "@web/core/dialog/dialog";
import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { View } from "@web/views/view";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

/**
 * @typedef {Object} Props
 * @property {import("@mail/core/common/thread_model").Thread} thread
 * @property {string} [className]
 * @extends {Component<Props, Env>}
 */
export class TemplateListPanel extends Component {
    static components = {
        ActionPanel,
        View,
    };
    static props = ["thread", "className?"];
    static template = "discuss.AgentListPanel";

    setup() {
        this.store = useService("mail.store");
        this.rpc = useService("rpc");
        const buttonTemplate = "web.FormViewDialog.ToMany.buttons";
        this.TemplateListService = useState(useService("discuss.TemplateListPanel"));
        debugger
        this.viewProps = {
            type: "list",
            buttonTemplate,
            context: {"partner": this.props.thread && this.props.thread.chatPartner && this.props.thread.chatPartner.id},
            display: { controlPanel: false },
            mode: "edit",
            resId: this.props.thread.chatPartner.id || false,
            resModel: 'wa.template',
            preventCreate: this.props.preventCreate,
            preventEdit: this.props.preventEdit,
            discardRecord: this.discardRecord.bind(this),
            saveRecord: async (record, { saveAndNew }) => {
                const saved = await record.save({ reload: false });
                if (saved) {
                    await this.props.onRecordSaved(record);
                    if (saveAndNew) {
                        const context = Object.assign({}, this.props.context);
                        Object.keys(context).forEach((k) => {
                            if (k.startsWith("default_")) {
                                delete context[k];
                            }
                        });
                        await record.model.load({ resId: false, context });
                    }
                }
                return saved;
            },
        };
    }

    async discardRecord() {
        if (this.props.onRecordDiscarded) {
            await this.props.onRecordDiscarded();
        }
    }

    /**
     * Prompt the user for confirmation and unpin the given message if
     * confirmed.
     *
     * @param {import('@mail/core/common/message_model').Message} message
     */
    onClickUnpin(message) {
        this.TemplateListService.unpin(message);
    }

    /**
     * Get the message to display when nothing is pinned on this thread.
     */
    get emptyText() {
        if (this.props.thread.type === "channel") {
            return _t("This channel doesn't have any pinned messages.");
        } else {
            return _t("This conversation doesn't have any pinned messages.");
        }
    }

    get title() {
        return _t("WhatsApp Templates");
    }
}

TemplateListPanel.props = {
    resModel: String,

    context: { type: Object, optional: true },
    mode: {
        optional: true,
        validate: (m) => ["edit", "readonly"].includes(m),
    },
    onRecordSaved: { type: Function, optional: true },
    onRecordDiscarded: { type: Function, optional: true },
    removeRecord: { type: Function, optional: true },
    resId: { type: [Number, Boolean], optional: true },
    title: { type: String, optional: true },
    viewId: { type: [Number, Boolean], optional: true },
    preventCreate: { type: Boolean, optional: true },
    preventEdit: { type: Boolean, optional: true },
    isToMany: { type: Boolean, optional: true },
    size: Dialog.props.size,
};
TemplateListPanel.defaultProps = {
    onRecordSaved: () => {},
    preventCreate: true,
    preventEdit: false,
    isToMany: false,
};