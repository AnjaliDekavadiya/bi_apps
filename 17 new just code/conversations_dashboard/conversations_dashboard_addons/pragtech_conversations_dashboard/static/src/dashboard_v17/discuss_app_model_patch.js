/* @odoo-module */

import { DiscussApp } from "@mail/core/common/discuss_app_model";
import { Record } from "@mail/core/common/record";

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(DiscussApp, {
    new(data) {
        const res = super.new(data);
        res.multi_livechat = {
            extraClass: "o-mail-DiscussSidebarCategory-multilivechat",
            id: "multi_livechat",
            name: _t("Whatsapp Chats"),
            isOpen: false,
            canView: false,
            canAdd: false,
            serverStateKey: "is_discuss_sidebar_category_multilivechat_open",
        };
        res.facebook_livechat = {
            extraClass: "o-mail-DiscussSidebarCategory-facebooklivechat",
            id: "facebook_livechat",
            name: _t("Facebook Chats"),
            isOpen: false,
            canView: false,
            canAdd: false,
            serverStateKey: "is_discuss_sidebar_category_facebooklivechat_open",
        };
        res.instagram_livechat = {
            extraClass: "o-mail-DiscussSidebarCategory-instagramlivechat",
            id: "instagram_livechat",
            name: _t("Instagram Chats"),
            isOpen: false,
            canView: false,
            canAdd: false,
            serverStateKey: "is_discuss_sidebar_category_instagramlivechat_open",
        };
        return res;
    },
});

patch(DiscussApp.prototype, {
    setup(env) {
        super.setup(env);
        this.multi_livechat = Record.one("DiscussAppCategory");
        this.facebook_livechat = Record.one("DiscussAppCategory");
        this.instagram_livechat = Record.one("DiscussAppCategory");
    },
});
