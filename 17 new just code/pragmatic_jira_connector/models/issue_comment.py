# -*- coding: utf-8 -*-

from odoo import fields, models
from dateutil import parser


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_auto_subscribe(self, updated_values, followers_existing_policy='skip'):
        """ Handle auto subscription. Auto subscription is done based on two
        main mechanisms

         * using subtypes parent relationship. For example following a parent record
           (i.e. project) with subtypes linked to child records (i.e. task). See
           mail.message.subtype ``_get_auto_subscription_subtypes``;
         * calling _message_auto_subscribe_notify that returns a list of partner
           to subscribe, as well as data about the subtypes and notification
           to send. Base behavior is to subscribe responsible and notify them;

        Adding application-specific auto subscription should be done by overriding
        ``_message_auto_subscribe_followers``. It should return structured data
        for new partner to subscribe, with subtypes and eventual notification
        to perform. See that method for more details.

        :param updated_values: values modifying the record trigerring auto subscription
        """
        if not self:
            return True

        new_partner_subtypes = dict()

        # return data related to auto subscription based on subtype matching (aka:
        # default task subtypes or subtypes from project triggering task subtypes)
        updated_relation = dict()
        child_ids, def_ids, all_int_ids, parent, relation = self.env[
            'mail.message.subtype']._get_auto_subscription_subtypes(self._name)

        # check effectively modified relation field
        for res_model, fnames in relation.items():
            for field in (fname for fname in fnames if updated_values.get(fname)):
                updated_relation.setdefault(res_model, set()).add(field)
        udpated_fields = [fname for fnames in updated_relation.values() for fname in fnames if
                          updated_values.get(fname)]

        if udpated_fields:
            # fetch "parent" subscription data (aka: subtypes on project to propagate on task)
            doc_data = [(model, [updated_values[fname] for fname in fnames]) for model, fnames in
                        updated_relation.items()]
            res = self.env['mail.followers']._get_subscription_data(doc_data, None, include_pshare=True,
                                                                    include_active=True)
            for _fol_id, _res_id, partner_id, subtype_ids, pshare, active in res:
                # use project.task_new -> task.new link
                sids = [parent[sid] for sid in subtype_ids if parent.get(sid)]
                # add checked subtypes matching model_name
                sids += [sid for sid in subtype_ids if sid not in parent and sid in child_ids]
                if partner_id and active:  # auto subscribe only active partners
                    if pshare:  # remove internal subtypes for customers
                        new_partner_subtypes[partner_id] = set(sids) - set(all_int_ids)
                    else:
                        new_partner_subtypes[partner_id] = set(sids)

        notify_data = dict()
        res = self._message_auto_subscribe_followers(updated_values, def_ids)
        for partner_id, sids, template in res:
            new_partner_subtypes.setdefault(partner_id, sids)
            if template:
                partner = self.env['res.partner'].browse(partner_id)
                lang = partner.lang if partner else None
                notify_data.setdefault((template, lang), list()).append(partner_id)

        self.env['mail.followers']._insert_followers(
            self._name, self.ids,
            list(new_partner_subtypes), subtypes=new_partner_subtypes,
            check_existing=True, existing_policy=followers_existing_policy)

        # notify people from auto subscription, for example like assignation
        for (template, lang), pids in notify_data.items():
            self.with_context(lang=lang)._message_auto_subscribe_notify(pids, template)

        return True


class Partner(models.Model):
    _inherit = 'res.partner'

    def _notify(self, message, force_send=False, send_after_commit=True, user_signature=True):
        if 'disable_mail_mail' in self.env.context:
            return True
        super(Partner, self)._notify(message, force_send, send_after_commit, user_signature)


class CommentOnIssue(models.Model):
    _inherit = 'mail.message'

    def receive_all(self, issue):
        int('a')

    def process_response(self, issue, response):
        formate_date = parser.parse(response['created']).strftime("%Y-%m-%d %H:%M:%S")
        formate_date = parser.parse(formate_date)
        updated_date = parser.parse(response['updated']).strftime("%Y-%m-%d %H:%M:%S")
        updated_date = parser.parse(updated_date)
        comment_dict = dict(
            jira_id=response['id'],
            author_id=self.env['res.users'].get_user_by_dict(response['author']).partner_id.id,
            update_author_id=self.env['res.users'].get_user_by_dict(response['updateAuthor']).partner_id.id,
            body=response['body'],
            date=formate_date,
            updated=updated_date,
            model='project.task',
            res_id=issue.id,
            message_type='comment',
            subtype_id=1,
        )
        comment = self.search([('jira_id', '=', comment_dict['jira_id'])])
        if not comment:
            comment = self.with_context(from_jira=True).create(comment_dict)
        else:
            comment.with_context(from_jira=True).write(comment_dict)
        return comment

    def key_operation(self, issue, id):
        pass

    jira_id = fields.Char()
    update_author_id = fields.Many2one('res.partner')
    updated = fields.Datetime()
