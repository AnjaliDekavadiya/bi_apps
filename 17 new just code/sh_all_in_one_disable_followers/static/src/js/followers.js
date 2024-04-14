/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { FollowerList } from "@mail/core/web/follower_list";
import { Chatter } from "@mail/core/web/chatter";


// FOR ADD FOLLOWERS WIZARD CONTEXT BUTTON ADD FOLLOWER ISSUE

patch(FollowerList.prototype, {
    onClickAddFollowers() {
        document.body.click(); // hack to close dropdown
        const action = {
            type: "ir.actions.act_window",
            res_model: "mail.wizard.invite",
            view_mode: "form",
            views: [[false, "form"]],
            name: _t("Invite Follower"),
            target: "new",
            context: {
                default_res_model: this.props.thread.model,
                default_res_id: this.props.thread.id,
                manually_added_follower: true,
            },
        };
        this.action.doAction(action, {
            onClose: () => {
                this.props.onAddFollowers?.();
            },
        });
    }
});

// FOR FOLLOW BUTTON ADD FOLLOWER ISSUE

patch(Chatter.prototype, {
    async _follow(threadModel, threadId) {
        await this.orm.call(threadModel, "message_subscribe", [[threadId]], {
            partner_ids: [this.store.self.id],
            // CUSTOM CHANGES FOR MANNUALLY CONTEXT
            context: { manually_added_follower: true },

        });
        this.onFollowerChanged();
    }
});
