/* @odoo-module */

import { WhatsappAutoresizeInput } from "@pragtech_conversations_dashboard/dashboard_v17/autoresize_input";
import { WhatsappComposer } from "@pragtech_conversations_dashboard/dashboard_v17/whatsapp_composer";
import { ImStatus } from "@mail/core/common/im_status";
import { WhatsappThread } from "@pragtech_conversations_dashboard/dashboard_v17/thread";
import { useThreadActions } from "@mail/core/common/thread_actions";
import { WhatsappThreadIcon } from "@pragtech_conversations_dashboard/dashboard_v17/whatsapp_thread_icon";
import { WhatsappSidebar } from "@pragtech_conversations_dashboard/dashboard_v17/whatsapp_sidebar"
import {
    useMessageEdition,
    useMessageHighlight,
    useMessageToReplyTo,
} from "@mail/utils/common/hooks";

import {
    Component,
    onWillStart,
    onMounted,
    onWillUnmount,
    useChildSubEnv,
    useRef,
    useState,
    useEffect,
    useExternalListener,
} from "@odoo/owl";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { FileUploader } from "@web/views/fields/file_handler";

export class Whatsapp extends Component {
    static components = {
        WhatsappAutoresizeInput,
        WhatsappThread,
        WhatsappThreadIcon,
        WhatsappComposer,
        FileUploader,
        ImStatus,
        WhatsappSidebar,
    };
    static props = {};
    static template = "whatsapp.Discuss";

    setup() {
        this.messaging = useState(useService("mail.messaging"));
        this.store = useState(useService("mail.store"));
        this.threadService = useState(useService("mail.thread"));
        this.personaService = useService("mail.persona");
        this.messageHighlight = useMessageHighlight();
        this.messageEdition = useMessageEdition();
        this.messageToReplyTo = useMessageToReplyTo();
        this.contentRef = useRef("content");
        this.root = useRef("root");
        this.state = useState({ jumpThreadPresent: 0 });
        this.orm = useService("orm");
        this.effect = useService("effect");
        this.ui = useState(useService("ui"));
        this.prevInboxCounter = this.store.discuss.inbox.counter;
        useChildSubEnv({
            inDiscussApp: true,
            messageHighlight: this.messageHighlight,
        });
        this.notification = useService("notification");
        this.threadActions = useThreadActions();
        useExternalListener(
            window,
            "keydown",
            (ev) => {
                if (getActiveHotkey(ev) === "escape" && !this.thread?.composer?.isFocused) {
                    if (this.thread?.composer) {
                        this.thread.composer.autofocus++;
                    }
                }
            },
            { capture: true }
        );
        useEffect(
            () => {
                if (
                    this.thread?.id === "inbox" &&
                    this.prevInboxCounter !== this.store.discuss.inbox.counter &&
                    this.store.discuss.inbox.counter === 0
                ) {
                    this.effect.add({
                        message: _t("Congratulations, your inbox is empty!"),
                        type: "rainbow_man",
                        fadeout: "fast",
                    });
                }
                this.prevInboxCounter = this.store.discuss.inbox.counter;
            },
            () => [this.store.discuss.inbox.counter]
        );
        onWillStart(() => this.messaging.isReady);
        onMounted(() => (this.store.discuss.isActive = true));
        onWillUnmount(() => (this.store.discuss.isActive = false));
    }

    get thread() {
        // console.log("threads===", this.store.discuss.thread)
        return this.store.discuss.thread;
    }

    async onFileUploaded(file) {
        await this.threadService.notifyThreadAvatarToServer(this.thread.id, file.data);
        this.notification.add(_t("The avatar has been updated!"), { type: "success" });
    }

    async renameThread(name) {
        await this.threadService.renameThread(this.thread, name);
    }

    async updateThreadDescription(description) {
        const newDescription = description.trim();
        if (!newDescription && !this.thread.description) {
            return;
        }
        if (newDescription !== this.thread.description) {
            await this.threadService.notifyThreadDescriptionToServer(this.thread, newDescription);
        }
    }

    async renameGuest(name) {
        const newName = name.trim();
        if (this.store.guest?.name !== newName) {
            await this.personaService.updateGuestName(this.store.self, newName);
        }
    }
}
