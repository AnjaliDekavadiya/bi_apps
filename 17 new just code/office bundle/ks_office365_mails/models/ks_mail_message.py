from odoo import models, fields, api, _, modules
from odoo.http import request


class KsMailMessage(models.Model):
    _inherit = 'mail.message'

    ks_cc = fields.Char("Ks Sent Mail Recipients", default=False)
    ks_bcc = fields.Char("Ks Sent Mail cc", default=False)
    ks_send_to = fields.Char("Ks Sent Mail bcc", default=False)

    # adding cc, bcc and send to to the message
    # @api.multi
    def message_format(self, format_reply=True, msg_vals=None):
        message_values = self.read([
            'id', 'body', 'date', 'author_id', 'email_from',  # base message fields
            'message_type', 'subtype_id', 'subject',  # message specific
            'model', 'res_id', 'record_name',  # document related
            'partner_ids',  # recipients
            'starred_partner_ids',  # list of partner ids for whom the message is starred
            'ks_send_to', 'ks_cc', 'ks_bcc',
        ])
        message_tree = dict((m.id, m) for m in self.sudo())
        self._message_read_dict_postprocess(message_values, message_tree)

        # add subtype data (is_note flag, is_discussiFon flag , subtype_description). Do it as sudo
        # because portal / public may have to look for internal subtypes
        subtype_ids = [msg['subtype_id'][0] for msg in message_values if msg['subtype_id']]
        subtypes = self.env['mail.message.subtype'].sudo().browse(subtype_ids).read(['internal', 'description', 'id'])
        subtypes_dict = dict((subtype['id'], subtype) for subtype in subtypes)

        com_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
        note_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        # fetch notification status
        notif_dict = {}
        notifs = self.env['mail.notification'].sudo().search(
            [('mail_message_id', 'in', list(mid for mid in message_tree)), ('is_read', '=', False)])
        for notif in notifs:
            mid = notif.mail_message_id.id
            if not notif_dict.get(mid):
                notif_dict[mid] = {'partner_id': list()}
            notif_dict[mid]['partner_id'].append(notif.res_partner_id.id)

        for message in message_values:
            # message['needaction_partner_ids'] = notif_dict.get(message['id'], dict()).get('partner_id', [])
            message['is_note'] = message['subtype_id'] and subtypes_dict[message['subtype_id'][0]]['id'] == note_id
            message['is_discussion'] = message['subtype_id'] and subtypes_dict[message['subtype_id'][0]]['id'] == com_id
            message['is_notification'] = message['is_note'] and not message['model'] and not message['res_id']
            message['subtype_description'] = message['subtype_id'] and subtypes_dict[message['subtype_id'][0]][
                'description']
            if message['model'] and self.env[message['model']]._original_module:
                message['module_icon'] = modules.module.get_module_icon(self.env[message['model']]._original_module)
        return message_values


    @api.model
    def _message_read_dict_postprocess(self, messages, message_tree):
        """ Post-processing on values given by message_read. This method will
            handle partners in batch to avoid doing numerous queries.

            :param list messages: list of message, as get_dict result
            :param dict message_tree: {[msg.id]: msg browse record as super user}
        """
        # 1. Aggregate partners (author_id and partner_ids), attachments and tracking values
        partners = self.env['res.partner'].sudo()
        attachments = self.env['ir.attachment']
        message_ids = list(message_tree.keys())
        email_notification_tree = {}
        # By rebrowsing all the messages at once, we ensure all the messages
        # to be on the same prefetch group, enhancing that way the performances
        for message in self.sudo().browse(message_ids):
            if message.author_id:
                partners |= message.author_id
            # find all notified partners
            email_notification_tree[message.id] = message.notification_ids.filtered(
                lambda n: n.notification_type == 'email' and n.res_partner_id.active and
                          (n.notification_status in (
                              'bounce', 'exception', 'canceled') or n.res_partner_id.partner_share))
            if message.attachment_ids:
                attachments |= message.attachment_ids
        partners |= self.env['mail.notification'].concat(*email_notification_tree.values()).mapped('res_partner_id')
        # Read partners as SUPERUSER -> message being browsed as SUPERUSER it is already the case
        partners_names = partners.getting_user_name()
        partner_tree = dict((partner[0], partner) for partner in partners_names)

        # 2. Attachments as SUPERUSER, because could receive msg and attachments for doc uid cannot see
        attachments_data = attachments.sudo().read(['id', 'name', 'mimetype'])
        safari = request and request.httprequest.user_agent.browser == 'safari'
        attachments_tree = dict((attachment['id'], {
            'id': attachment['id'],
            'filename': attachment['name'],
            'name': attachment['name'],
            'mimetype': 'application/octet-stream' if safari and attachment['mimetype'] and 'video' in attachment[
                'mimetype'] else attachment['mimetype'],
        }) for attachment in attachments_data)

        # 3. Tracking values
        tracking_values = self.env['mail.tracking.value'].sudo().search([('mail_message_id', 'in', message_ids)])
        message_to_tracking = dict()
        tracking_tree = dict.fromkeys(tracking_values.ids, False)
        for tracking in tracking_values:
            groups = tracking.field_groups
            if not groups or self.env.is_superuser() or self.user_has_groups(groups):
                message_to_tracking.setdefault(tracking.mail_message_id.id, list()).append(tracking.id)
                tracking_tree[tracking.id] = {
                    'id': tracking.id,
                    'changed_field': tracking.field_desc,
                    'old_value': tracking._get_old_display_value()[0],
                    'new_value': tracking._get_new_display_value()[0],
                    'field_type': tracking.field_type,
                }

        # 4. Update message dictionaries
        for message_dict in messages:
            message_id = message_dict.get('id')
            message = message_tree[message_id]
            if message.author_id:
                author = partner_tree[message.author_id.id]
            else:
                author = (0, message.email_from)
            customer_email_status = (
                    (all(n.notification_status == 'sent' for n in message.notification_ids if
                         n.notification_type == 'email') and 'sent') or
                    (any(n.notification_status == 'exception' for n in message.notification_ids if
                         n.notification_type == 'email') and 'exception') or
                    (any(n.notification_status == 'bounce' for n in message.notification_ids if
                         n.notification_type == 'email') and 'bounce') or
                    'ready'
            )
            customer_email_data = []
            for notification in email_notification_tree[message.id]:
                customer_email_data.append((partner_tree[notification.res_partner_id.id][0],
                                            partner_tree[notification.res_partner_id.id][1],
                                            notification.notification_status))

            attachment_ids = []
            main_attachment = False
            if message.attachment_ids:
                has_access_to_model = message.model and self.env[message.model].check_access_rights('read',
                                                                                                    raise_exception=False)
                if message.res_id and issubclass(self.pool[message.model],
                                                 self.pool['mail.thread.main.attachment']) and has_access_to_model:
                    main_attachment = self.env[message.model].browse(message.res_id).message_main_attachment_id
                for attachment in message.attachment_ids:
                    if attachment.id in attachments_tree:
                        attachments_tree[attachment.id]['is_main'] = main_attachment == attachment
                        attachment_ids.append(attachments_tree[attachment.id])

            tracking_value_ids = []
            for tracking_value_id in message_to_tracking.get(message_id, list()):
                if tracking_value_id in tracking_tree:
                    tracking_value_ids.append(tracking_tree[tracking_value_id])

            message_dict.update({
                'author_id': author,
                'customer_email_status': customer_email_status,
                'customer_email_data': customer_email_data,
                'attachment_ids': attachment_ids,
                'tracking_value_ids': tracking_value_ids,
            })

        return True


    def ks_get_fields_data(self, id):
        res = self.browse(id)
        ks_dict = {
            'ks_partner_ids': res.author_id.id,
            'ks_cc': res.ks_cc,
            'ks_bcc': res.ks_bcc,
            'ks_send_to': res.ks_send_to,
        }

        return ks_dict


class KsResPartner(models.Model):
    _inherit = 'res.partner'

    def getting_user_name(self):
        return [(record.id, record.display_name) for record in self]
