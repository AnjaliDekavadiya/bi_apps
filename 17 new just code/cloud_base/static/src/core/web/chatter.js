/** @odoo-module **/

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { CloudJsTreeContainer } from "@cloud_base/components/cloud_jstree_container/cloud_jstree_container";
import { onWillUpdateProps, onWillStart, useState } from "@odoo/owl";


patch(Chatter.prototype, {
    /*
    * Re-write to check folder existance on chatter update
    */
    setup() {
        super.setup(...arguments);
        this.state = useState({ folderExist: false });
        this.cloudsFolderId = false;
        onWillStart(async () => {
            await this.onCheckFolder(this.props);
        });
        onWillUpdateProps(async (nextProps) => {
            await this.onCheckFolder(nextProps);
        });
    },
    /*
    * The method to check whether the current folder exists
    */
    async onCheckFolder(nextProps) {
        const folderExist = await this.rpc(
            "/cloud_base/folder",
            { thread_id: nextProps.threadId, thread_model: nextProps.threadModel },
        );
        this.state.folderExist = folderExist;
    },
    /*
    * Re-write to show the attachment box disregarding whether it has or not attachments
    */
    onClickAddAttachments() {
        if (this.attachments.length === 0) {
            this.state.isAttachmentBoxOpened = !this.state.isAttachmentBoxOpened;
            if (this.state.isAttachmentBoxOpened) {
                this.state.scrollToAttachments++;
            };
        };
        super.onClickAddAttachments(...arguments)
    },
    /*
    * The method to prepare jstreecontainer props
    */
    getJsTreeProps(key) {
        return {
            jstreeId: key,
            onUpdateSearch: this.onRefreshAttachmentBoxWithFolder.bind(this),
            kanbanView: false,
            parentModel: this,
            resModel: this.props.threadModel,
            resId: this.props.threadId,
        }
    },
    /*
    * The method to prepare the domain by the JScontainer and notify searchmodel
    */
    async onRefreshAttachmentBoxWithFolder(jstreeId, domain) {
        if (this.state.thread) {
            this.threadService.refreshFolderAttachments(this.state.thread, domain, this.cloudsFolderId)
        }
    },
});

Chatter.components = {
    ...Chatter.components,
    CloudJsTreeContainer,
};
