/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from '@web/core/l10n/translation';

const { Component, onWillStart, onMounted, onWillDestroy, useState, useRef } = owl;
const { DateTime } = luxon;


export class MailInbox extends Component {
    setup() {
        this.state = useState({
            emailList: [],
            markAsReadList: [],
            isMarkAsDeleteList: [],
            isMarkAsArchiveList: [],
            allEmailsList: [],
            mailBoxContainer: 'inbox',
            offset: 0,
            limit: 20,
            total: 0,
            searchDomain: [],
            allowSaveToDraft: true,
            saveToDraftID: 0,
        })
        this.mailForm = useRef("eMail-Form");
        this.ckInstance = false;
        this.emailSearchInput = useRef("email-search-input");
        this.searchClearbtn = useRef("clear-button");
        this.model = "mail.inbox";
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.http = useService("http");
        if (!this.autoFetchMailInterval) {
            this.autoFetchMailInterval = setInterval(this._refreshResults.bind(this), 30000);
        }
        onWillStart(async ()=> {
            this.state.mailBoxContainer = 'inbox';
            this.getMailList(false, false);
            this.getAllEmailsList();
        });
        onMounted(this._onMounted.bind(this));
        onWillDestroy(async () => {
            if (this.autoFetchMailInterval) {
                clearInterval(this.autoFetchMailInterval);
            }
            await this.onClickMailClose();
        });
    }
    async _onMounted() {
        var self = this;
        if ($(this.mailForm.el).find('#message') && $(this.mailForm.el).find('#message').length) {
            const editorConfig = {
                toolbar: {
                    items: [
                        'undo', 'redo', '|',
                        'heading', '|',
                        'bold', 'italic', 'underline', '|',
                        'bulletedList', 'numberedList', '|',
                        'alignment', '|',
                        'insertTable', '|',
                        'sourceEditing'
                    ],
                    shouldNotGroupWhenFull: true
                },
                list: {
                    properties: {
                        styles: true,
                        startIndex: true,
                        reversed: true
                    }
                },
                heading: {
                    options: [
                        { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                        { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                        { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
                        { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
                        { model: 'heading4', view: 'h4', title: 'Heading 4', class: 'ck-heading_heading4' },
                        { model: 'heading5', view: 'h5', title: 'Heading 5', class: 'ck-heading_heading5' },
                        { model: 'heading6', view: 'h6', title: 'Heading 6', class: 'ck-heading_heading6' }
                    ]
                },
                htmlSupport: {
                    allow: [
                        {
                            name: /.*/,
                            attributes: true,
                            classes: true,
                            styles: true
                        }
                    ]
                },
                removePlugins: [
                    'CKBox',
                    'CKFinder',
                    'EasyImage',
                    'RealTimeCollaborativeComments',
                    'RealTimeCollaborativeTrackChanges',
                    'RealTimeCollaborativeRevisionHistory',
                    'PresenceList',
                    'Comments',
                    'TrackChanges',
                    'TrackChangesData',
                    'RevisionHistory',
                    'Pagination',
                    'WProofreader',
                    'MathType',
                    'SlashCommand',
                    'Template',
                    'DocumentOutline',
                    'FormatPainter',
                    'TableOfContents'
                ]
            }
            CKEDITOR.ClassicEditor.create($(this.mailForm.el).find('#message')[0], editorConfig)
            .then( editor => {
                self.ckInstance = editor;
                const editorElement = editor.ui.view.editable.element;
                editorElement.addEventListener('keydown', event => {
                    if (event.keyCode == 32) {
                        event.preventDefault();
                        const currentPosition = editor.model.document.selection.getFirstPosition();
                        editor.model.change(writer => {
                            writer.insertText(' ', currentPosition);
                        });
                    }
                });
                editor.model.document.on('change:data', (evt, data) => {
                    const txt = editor.getData();
                    $(self.mailForm.el).find('#message').val(txt);
                });
            })
            .catch( error => {
                console.error( error );
            } );
        }
        this.attachSelect2();
    }
    get minimum() {
        return this.state.offset + 1;
    }
    get maximum() {
        return Math.min(this.state.offset + this.state.limit, this.state.total);
    }
    get value() {
        const parts = [this.minimum];
        if (this.state.limit > 1) {
            parts.push(this.maximum);
        }
        return parts.join("-");
    }
    formatDateString(actualDate) {
        try {
            const today = DateTime.local();
            const emailDate = DateTime.fromFormat(actualDate, 'yyyy-MM-dd HH:mm:ss', { zone: 'utc' }).toLocal();

            if (emailDate.hasSame(today, 'day')) {
                return emailDate.toFormat('hh:mm a');
            } else if (emailDate < today.startOf('year')) {
                return emailDate.toFormat('dd LLL yyyy hh:mm a');
            } else {
                return emailDate.toFormat('dd LLL hh:mm a');
            }
        } catch (error) {
            console.error('Error parsing date:', actualDate, error.message);
            // Handle the error or return a default value
            return 'Invalid Date';
        }
    }

    htmlToPlainText(html) {
        let plainText = '';
        try {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            if (tempDiv) {
                const styleElements = tempDiv.querySelectorAll('style');
                styleElements.forEach((styleElement) => {
                    styleElement.remove();
                });
            }
            plainText = tempDiv.textContent || tempDiv.innerText;
            plainText = plainText.trim();
            plainText = plainText.replace(/[\s­͏]+/gu, ' ');
            return plainText;
        } catch {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            plainText = tempDiv.textContent || tempDiv.innerText;
            return plainText;
        }
    }
    titleCase(str) {
        var splitStr = str.toLowerCase().split(' ');
        for (var i = 0; i < splitStr.length; i++) {
            splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
        }
        return splitStr.join(' ');
    }
    async navigate(direction) {
        let minimum = this.state.offset + this.state.limit * direction;
        let total = this.state.total;
        if (minimum >= total) {
                minimum = 0;
        } else if (minimum < 0 && this.state.limit === 1) {
            minimum = total - 1;
        } else if (minimum < 0 && this.state.limit > 1) {
            minimum = total - (total % this.state.limit || this.state.limit);
        }
        this.update(minimum, this.state.limit, true);
    }
    async update(offset, limit, hasNavigated) {
        await this.onUpdate({ offset, limit }, hasNavigated);
        await this.getMailList(false, false);
    }
    async onUpdate({ offset, limit }, hasNavigated) {
        this.state.offset = offset;
        this.state.limit = limit;
    }
    onKeyPress(ev) {
        if (ev.keyCode === 13 || ev.which === 13) {
            ev.preventDefault();
            this.onClickSearchEmail(ev);
        }
        const searchVal = this.emailSearchInput.el.value;
        if (!searchVal) {
            this.state.searchDomain = [];
        }
    }
    onKeyUp(ev) {
        const searchVal = this.emailSearchInput.el.value;
        if (searchVal === '') {
            this.searchClearbtn.el.style.opacity = 0;
        } else {
            this.searchClearbtn.el.style.opacity = 1;
        }
    }
    async onClickSearchClear(ev) {
        this.emailSearchInput.el.value = '';
        this.state.searchDomain = [];
        await this.getMailList(false, false);
    }
    async onClickSearchEmail(ev) {
        const searchVal = this.emailSearchInput.el.value;
        if (!searchVal) {
            this.state.searchDomain = [];
        } else {
            var domainSubject = ['subject', 'ilike', searchVal];
            this.state.searchDomain.push('|', '|', domainSubject);
            var domainBody = ['body_content', 'ilike', searchVal];
            this.state.searchDomain.push(domainBody);
            var domainSenderName = ['email_from_name', 'ilike', searchVal];
            this.state.searchDomain.push(domainSenderName);
        }
        await this.getMailList(false, false);
    }
    async _refreshResults () {
        this.getMailList(false, false);
    }
    attachSelect2(customEmails=false) {
        if (!this.state.allEmailsList.length) {
            return;
        }
        var data = this.state.allEmailsList.map((val) => {
            return {id: val.email, text: val.name + " (" + val.email + ")"};
        });
        if (customEmails && customEmails.length) {
            customEmails.forEach(function(customEmail) {
                if (customEmail) {
                    const emailExist = data.some(e => e.id == customEmail);
                    if(!emailExist) {
                      data.push({'id': customEmail, text: customEmail})
                    }
                }
            });
        }
        $(this.mailForm.el).find("#o_email_recipient, #o_email_cc, #o_email_bcc").select2({
            placeholder: "Enter Recipients",
            allowClear: true,
            createSearchChoice: function (term) {
                return {id: term, text: term};
            },
            createSearchChoicePosition: 'bottom',
            multiple: true,
            tags: true,
            tokenSeparators: [',', ' '],
            data: data,
            minimumInputLength: 3,
            maximumInputLength: 255,
            language: {
                inputTooShort: function(args) {
                    return '';
                }
            },
        });
    }
    async onClickMailCreate(ev) {
        const mailComposer = document.getElementsByClassName('o_mail_composer');
        if (mailComposer.length) {
            await this.attachSelect2();
            mailComposer[0].classList.remove('o_hidden');
            const ccVal = $(this.mailForm.el).find("#o_email_cc").val();
            if (!ccVal) {
                $(this.mailForm.el).find('#o_email_cc').addClass('o_hidden');
            }
            const bccVal = $(this.mailForm.el).find("#o_email_bcc").val();
            if (bccVal) {
                $(this.mailForm.el).find('#o_email_bcc').addClass('o_hidden');
            }
        }
    }
    async onClickMailClose(ev, saveToDraft=false) {
        const mailComposer = document.getElementsByClassName('o_mail_composer');
        if (mailComposer.length) {
            mailComposer[0].classList.add('o_hidden');
        }
        if ($(this.mailForm.el).length) {
            const emailRecipient = $(this.mailForm.el).find("#o_email_recipient");
            const emailBCC =  $(this.mailForm.el).find("#o_email_bcc");
            const emailSubject = $(this.mailForm.el).find("#subject");
            const emailCC =  $(this.mailForm.el).find("#o_email_cc");
            if (saveToDraft){
                const emailBody =  $(this.mailForm.el).find("#message");
                const emailAttachments =  $(this.mailForm.el).find("#attachment");
                const emailValues = [emailRecipient.val(), emailSubject.val(), emailCC.val(), emailBCC.val(), emailBody.val(), emailAttachments[0].files];
                const hasValues = emailValues.some(value => Boolean(value));
                if (hasValues) {
                    await this.saveToDraft(emailValues);
                }
            }
            $(this.mailForm.el)[0].reset();
            emailRecipient.select2("val", "");
            emailCC.select2("val", "");
            emailBCC.select2("val", "");
            $(this.mailForm.el).find("#message").val('');
            if (this.ckInstance) {
                this.ckInstance.setData('');
            }
        }
    }
    async saveToDraft(emailValues) {
        var mailValues = {
            "email_to": emailValues[0],
            "subject": emailValues[1],
            "email_cc": emailValues[2],
            "email_bcc": emailValues[3],
            "body_html": emailValues[4],
            "state": "draft",
        }
        var resID = 0;
        if (this.state.allowSaveToDraft) {
            resID = await this.orm.create(this.model, [mailValues]);
        } else {
            resID = this.state.saveToDraftID;
            await this.orm.write(this.model, [resID], mailValues);
        }
        const fileData = await this.http.post(
            "/web/binary/upload_attachment",
            {
                csrf_token: odoo.csrf_token,
                ufile: [...emailValues[5]],
                model: this.model,
                id: resID,
            },
            "text"
        );
        const parsedFileData = JSON.parse(fileData);
        if (parsedFileData.error) {
            throw new Error(parsedFileData.error);
        }
        const attachment_ids = parsedFileData.map((file) => file.id)
        const isSent = await this.orm.call(this.model, 'email_send', [resID, attachment_ids, false]);
        this.getMailList(false, false);
    }
    validateEmail(email) {
        const pattern = /^[\w.-]+@[\w.-]+\.\w+$/;
        return pattern.test(email);
    }
    removeInvalidEmails(emails) {
        const emailArray = emails.split(',');
        var self = this;
        const validEmails = emailArray.filter((email) => self.validateEmail(email.trim()));
        return validEmails.join(',');
    }
    async onSendEmail() {
        var emails = $(this.mailForm.el).find('#o_email_recipient').val();
        var validEmails = this.removeInvalidEmails(emails);
        var cc = $(this.mailForm.el).find('#o_email_cc').val();
        var validCc = this.removeInvalidEmails(cc);
        var bcc = $(this.mailForm.el).find('#o_email_bcc').val();
        var validBcc = this.removeInvalidEmails(bcc);
        var subject = $(this.mailForm.el).find('#subject').val();
        var body = $(this.mailForm.el).find('#message').val();
        var attachment = $(this.mailForm.el).find('#attachment');
        var attachments = attachment && attachment[0].files;
        var mailValues = {
            "subject": subject,
            "email_to": validEmails,
            "email_cc": validCc,
            "email_bcc": validBcc,
            "body_html": body,
        }
        const resID = await this.orm.create(this.model, [mailValues]);
        const fileData = await this.http.post(
            "/web/binary/upload_attachment",
            {
                csrf_token: odoo.csrf_token,
                ufile: [...attachments],
                model: this.model,
                id: resID,
            },
            "text"
        );
        const parsedFileData = JSON.parse(fileData);
        if (parsedFileData.error) {
            throw new Error(parsedFileData.error);
        }
        const attachment_ids = parsedFileData.map((file) => file.id)
        const isSent = await this.orm.call(this.model, 'email_send', [resID, attachment_ids]);
        if (isSent) {
            let message = _t('Mail sent.');
            this.env.services.notification.add(message, {
                type: 'info',
                sticky: false,
            });
            await this.onClickMailClose();
        } else {
            let message = _t('Failed! Email not sent.');
            this.env.services.notification.add(message, {
                type: 'danger',
                sticky: false,
            });
        }
    }
    async onClickCC(ev) {
        $(this.mailForm.el).find('#o_email_cc').removeClass('o_hidden');
    }
    async onClickBCC(ev) {
        $(this.mailForm.el).find('#o_email_bcc').removeClass('o_hidden');
    }
    async getMailList(ev, fetchMail=false) {
        var $target = false;
        if (ev) {
            $target = $(ev.currentTarget);
        }
        if ($target) {
            $target.find("i").addClass("fa-spin");
        }
        if (fetchMail) {
            await this.orm.call(this.model, 'fetch_all_emails', []);
        }

        const fields = [
            "id",
            "email_to",
            "email_cc",
            "email_bcc",
            "subject",
            "body_html",
            "email_from_name",
            "email_to_name",
            "date",
            "is_read",
            "attachment_count",
            "attachment_ids",
            "state",
            "profile_pic",
        ];
        const states = {
            'inbox': 'received',
            'draft': 'draft',
            'outbox': 'outgoing',
            'sent': 'sent',
            'archive': 'archived',
            'trash': 'trash',
        }
        const currentState = states[this.state.mailBoxContainer];
        const domain = ['state', '=', currentState];
        this.state.searchDomain.push(domain);
        const mailList = await this.orm.searchRead(this.model,
            this.state.searchDomain,
            fields,
            {
                offset: this.state.offset,
                limit: this.state.limit,
                order: 'id DESC',
            }
        );
        var countDomain = []
        if (this.state.searchDomain.length) {
            countDomain = this.state.searchDomain;
        } else {
            countDomain.push(domain);
        }
        this.state.total = await this.orm.searchCount(this.model, countDomain);
        this.state.emailList = mailList;
        if (ev) {
            $target.find("i").removeClass("fa-spin");
        }
    }
    async getAllEmailsList() {
        const fields = ["name", "email"];
        this.state.allEmailsList = await this.orm.searchRead("res.partner", [["email", "!=", false]], fields);
    }
    async onClickEmailRow(email) {
        if (email && email.id) {
            this.markAsRead([email.id]);
            return this.actionService.doAction({
                type: 'ir.actions.act_window',
                res_model: "mail.inbox",
                res_id: email.id,
                views: [[false, "form"]],
                view_mode: "form",
                target: "current",
            });
        }
    }
    async onClickRestoreDraft(email) {
        const mailComposer = document.getElementsByClassName('o_mail_composer');
        if (mailComposer.length) {
            const customEmails = [email.email_to, email.email_cc, email.email_bcc]
            await this.attachSelect2(customEmails);
            if (email.id) {
                this.state.allowSaveToDraft = false;
                this.state.saveToDraftID = email.id;
            }
            mailComposer[0].classList.remove('o_hidden');
            $(this.mailForm.el).find("#o_email_recipient").val(email.email_to).trigger('change');
            $(this.mailForm.el).find("#o_email_cc").val(email.email_cc).trigger('change');
            $(this.mailForm.el).find("#o_email_bcc").val(email.email_bcc).trigger('change');
            $(this.mailForm.el).find("#subject").val(email.subject);
            $(this.mailForm.el).find("#message").val(email.body_html);
            const ccVal = $(this.mailForm.el).find("#o_email_cc").val();
            if (!ccVal) {
                $(this.mailForm.el).find('#o_email_cc').addClass('o_hidden');
            } else {
                $(this.mailForm.el).find('#o_email_cc').removeClass('o_hidden');
            }
            const bccVal = $(this.mailForm.el).find("#o_email_bcc").val();
            if (!bccVal) {
                $(this.mailForm.el).find('#o_email_bcc').addClass('o_hidden');
            } else {
                $(this.mailForm.el).find('#o_email_bcc').removeClass('o_hidden');
            }
            var attachmentInput =  $(this.mailForm.el).find("#attachment");
            if (email.attachment_count) {
                const fields = ['name', 'datas', 'mimetype'];
                const irAttchments = await this.orm.searchRead("ir.attachment", [["res_model", "=", this.model], ["res_id", "=", email.id]], fields);
                if (irAttchments) {
                    var dataTransfer = new DataTransfer();
                    irAttchments.forEach(function(att) {
                        var binaryContent = atob(att.datas);
                        var uint8Array = new Uint8Array(binaryContent.length);
                        for (var i = 0; i < binaryContent.length; i++) {
                            uint8Array[i] = binaryContent.charCodeAt(i);
                        }
                        var blob = new Blob([uint8Array], { type: att.mimetype});
                        var file = new File([blob], att.name);
                        dataTransfer.items.add(file);
                    });
                    attachmentInput[0].files = dataTransfer.files;
                }
            }
        }
    }
    async onClickmarkAsRead() {
        const resIds = this.state.markAsReadList;
        if (resIds.length) {
            this.markAsRead(resIds)
        }
    }
    async markAsRead(resIds, markOnServer=false) {
        const context = {'mark_on_server': markOnServer};
        await this.orm.write(this.model, resIds, {'is_read': true}, { context });
        await this.getMailList();
    }
    async markAsUnread(resIds, markOnServer=false) {
        const context = {'mark_on_server': markOnServer};
        await this.orm.write(this.model, resIds, {'is_read': false}, { context });
        await this.getMailList();
    }
    async onClickDelete(resID=false, forver=false) {
        var resIds = [];
        if (resID) {
            resIds.push(resID)
        } else {
            resIds = this.state.isMarkAsDeleteList;
        }
        if (resIds.length) {
            if (forver) {
                await this.orm.unlink(this.model, resIds);
            } else {
                await this.orm.write(this.model, resIds, {'state': 'trash'});
            }
            await this.getMailList();
        }
    }
    async onClickArchiveBtn(resID=false) {
        var resIds = [];
        if (resID) {
            resIds.push(resID)
        } else {
            resIds = this.state.isMarkAsArchiveList;
        }
        if (resIds.length) {
            await this.orm.write(this.model, resIds, {'state': 'archived'});
            await this.getMailList();
        }
    }
    onChangeCheckAll(ev) {
        if (!ev) {
            return;
        }
        var $target = $(ev.currentTarget);
        var self = this;
        if ($target && $target.length && $target[0].checked) {
            var $inputs = $target.closest('.inbox-body').find('.o_mail_box_table').find('.o_mail_inbox_line').prop('checked', true);
            for (const input of $inputs) {
                const emailID = parseInt(input.getAttribute('email-id') || '');
                const emailIsRead = input.getAttribute('email-is_read');
                if (!emailID) {
                    return;
                }
                if (input.checked) {
                    if (!self.state.isMarkAsDeleteList.includes(emailID)) {
                        self.state.isMarkAsDeleteList.push(emailID)
                    }
                    if (!self.state.isMarkAsArchiveList.includes(emailID)) {
                        self.state.isMarkAsArchiveList.push(emailID)
                    }
                    if (!emailIsRead) {
                        if (!self.state.markAsReadList.includes(emailID)) {
                            self.state.markAsReadList.push(emailID)
                        }
                    }
                }

            }
        } else {
            var $inputs = $target.closest('.inbox-body').find('.o_mail_box_table').find('.o_mail_inbox_line').prop('checked', false);
            for (const input of $inputs) {
                const emailID = parseInt(input.getAttribute('email-id') || '');
                if (!input.checked) {
                    if (self.state.isMarkAsDeleteList.includes(emailID)) {
                      const index = self.state.isMarkAsDeleteList.indexOf(emailID);
                      self.state.isMarkAsDeleteList.splice(index, 1);
                    }
                    if (self.state.isMarkAsArchiveList.includes(emailID)) {
                      const index = self.state.isMarkAsArchiveList.indexOf(emailID);
                      self.state.isMarkAsArchiveList.splice(index, 1);
                    }
                    if (self.state.markAsReadList.includes(emailID)) {
                      const index = self.state.markAsReadList.indexOf(emailID);
                      self.state.markAsReadList.splice(index, 1);
                    }
                }
            }
        }
    }
    onChangeMailLine(ev, email) {
        const checkBox = ev.currentTarget;
        if (!email || !email.id) {
            return false;
        }
        if (checkBox.checked) {
            if (!this.state.isMarkAsDeleteList.includes(email.id)) {
                this.state.isMarkAsDeleteList.push(email.id)
            }
            if (!this.state.isMarkAsArchiveList.includes(email.id)) {
                this.state.isMarkAsArchiveList.push(email.id)
            }
            if (!email.is_read) {
                if (!this.state.markAsReadList.includes(email.id)) {
                    this.state.markAsReadList.push(email.id)
                }
            }
        } else {
            if (this.state.isMarkAsDeleteList.includes(email.id)) {
              const index = this.state.isMarkAsDeleteList.indexOf(email.id);
              this.state.isMarkAsDeleteList.splice(index, 1);
            }
            if (this.state.isMarkAsArchiveList.includes(email.id)) {
              const index = this.state.isMarkAsArchiveList.indexOf(email.id);
              this.state.isMarkAsArchiveList.splice(index, 1);
            }
            if (this.state.markAsReadList.includes(email.id)) {
              const index = this.state.markAsReadList.indexOf(email.id);
              this.state.markAsReadList.splice(index, 1);
            }
        }
    }
    onClickInbox() {
        this.state.mailBoxContainer = 'inbox';
        this.resetCheckboxState();
        this.getMailList();
    }
    onClickDraft() {
        this.state.mailBoxContainer = 'draft';
        this.resetCheckboxState();
        this.getMailList();
    }
    onClickOutbox() {
        this.state.mailBoxContainer = 'outbox';
        this.resetCheckboxState();
        this.getMailList();
    }
    onClickSent() {
        this.state.mailBoxContainer = 'sent';
        this.resetCheckboxState();
        this.getMailList();
    }
    onClickArchive() {
        this.state.mailBoxContainer = 'archive';
        this.resetCheckboxState();
        this.getMailList();
    }
    onClickTrash() {
        this.state.mailBoxContainer = 'trash';
        this.resetCheckboxState();
        this.getMailList();
    }
    resetCheckboxState() {
        this.state.markAsReadList = [];
        this.state.isMarkAsDeleteList = [];
        this.state.isMarkAsArchiveList = [];
        this.state.searchDomain = [];
    }
    async onClickOdooChat() {
        this.state.mailBoxContainer = 'odoo_chat';
        this.resetCheckboxState();
        return this.actionService.doAction({
            type: 'ir.actions.client',
            tag: 'mail.action_discuss',
            target: "main",
        });
    }
}
MailInbox.template = "is_mail_inbox.MailInbox"
registry.category("actions").add("is_mail_inbox.action_mail_inbox", MailInbox);
