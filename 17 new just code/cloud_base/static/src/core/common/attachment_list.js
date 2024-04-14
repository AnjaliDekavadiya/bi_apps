/** @odoo-module **/

import { AttachmentList } from "@mail/core/common/attachment_list";
import { patch } from "@web/core/utils/patch";


patch(AttachmentList.prototype, {
    /*
    * Re-write to make any synced attachments to be not image even if it is
    */
    get nonImagesAttachments() {
        return this.props.attachments.filter((attachment) => !attachment.isImage || attachment.cloudSynced);
    },
    /*
    * Re-write to make any synced attachments to be not image even if it is
    */
    get imagesAttachments() {
        return this.props.attachments.filter((attachment) => attachment.isImage && !attachment.cloudSynced);
    },
    /*
    * The method is introduced instead of this.fileViewer.open(attachment, props.attachments) in template
    * The goal is to open cloud URLs when that is possible
    */
    onPreviewOpen(file, files) {
        if (!file.cloudSynced || file.isViewable) {
            return this.fileViewer.open(file, files);
        }
        else {
            this.onClickOpenCloudLink(file);
        }
    },
    /*
    * The method to open the cloud URL if any
    */
    onClickOpenCloudLink(attachment) {
        const cloudLink = document.createElement("a");
        cloudLink.setAttribute("href", attachment.cloudURL);
        cloudLink.setAttribute("target", "_blank");
        cloudLink.click();
    },
});
