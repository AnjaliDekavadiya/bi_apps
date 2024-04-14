# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import logging
try:
	from xmlrpc import client as xmlrpclib
except ImportError:
	import xmlrpclib
from odoo import _, api, exceptions, fields, models, tools
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)


class MailThreadInherit(models.AbstractModel):

	_inherit = "mail.thread"

	@api.returns('mail.message', lambda value: value.id)
	def my_message_post(self, body='', subject=None,
					 message_type='notification', subtype=None,
					 parent_id=False, attachments=None,
					 notif_layout=False, add_sign=False, model_description=False,
					 mail_auto_delete=True, **kwargs):
		if attachments is None:
			attachments = {}
		if self.ids and not self.ensure_one():
			raise exceptions.ValidationError(_('Invalid record set: should be called as model (without records) or on single-record recordset'))
		model = False
		if self.ids:
			self.ensure_one()
			model = kwargs.get('model', False) if self._name == 'mail.thread' else self._name
			if model and model != self._name and hasattr(self.env[model], 'my_message_post'):
				return self.env[model].browse(self.ids).my_message_post(
					body=body, subject=subject, message_type=message_type,
					subtype=subtype, parent_id=parent_id, attachments=attachments,
					notif_layout=notif_layout, add_sign=add_sign,
					mail_auto_delete=mail_auto_delete, model_description=model_description, **kwargs)

		author_id = kwargs.get('author_id')
		if author_id is None:  # keep False values
			author_id = self.env['mail.message']._get_default_author().id
		partner_ids = set()
		kwargs_partner_ids = kwargs.pop('partner_ids', [])
		for partner_id in kwargs_partner_ids:
			if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
				partner_ids.add(partner_id[1])
			if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
				partner_ids |= set(partner_id[2])
			elif isinstance(partner_id, pycompat.integer_types):
				partner_ids.add(partner_id)
			else:
				pass  # we do not manage anything else
		if parent_id and not model:
			parent_message = self.env['mail.message'].browse(parent_id)
			private_followers = set([partner.id for partner in parent_message.partner_ids])
			if parent_message.author_id:
				private_followers.add(parent_message.author_id.id)
			private_followers -= set([author_id])
			partner_ids |= private_followers

		# 4: mail.message.subtype
		subtype_id = kwargs.get('subtype_id', False)
		if not subtype_id:
			subtype = subtype or 'mt_note'
			if '.' not in subtype:
				subtype = 'mail.%s' % subtype
			subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)

		# automatically subscribe recipients if asked to
		if self._context.get('mail_post_autofollow') and self.ids and partner_ids:
			partner_to_subscribe = partner_ids
			if self._context.get('mail_post_autofollow_partner_ids'):
				partner_to_subscribe = [p for p in partner_ids if p in self._context.get('mail_post_autofollow_partner_ids')]
			self.message_subscribe(list(partner_to_subscribe))


		MailMessage = self.env['mail.message']
		if self._mail_flat_thread and model and not parent_id and self.ids:
			messages = MailMessage.search(['&', ('res_id', '=', self.ids[0]), ('model', '=', model)], order="id ASC", limit=1)
			parent_id = messages.ids and messages.ids[0] or False
		# we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
		elif parent_id:
			messages = MailMessage.sudo().search([('id', '=', parent_id), ('parent_id', '!=', False)], limit=1)
			processed_list = []
			if messages:
				message = messages[0]
				while (message.parent_id and message.parent_id.id not in processed_list):
					processed_list.append(message.parent_id.id)
					message = message.parent_id
				parent_id = message.id

		values = kwargs
		values.update({
			'author_id': author_id,
			'model': model,
			'res_id': model and self.ids[0] or False,
			'body': body,
			'subject': subject or False,
			'message_type': message_type,
			'parent_id': parent_id,
			'subtype_id': subtype_id,
			'partner_ids': [(4, pid) for pid in partner_ids],
			'channel_ids': kwargs.get('channel_ids', []),
			'add_sign': add_sign
		})
		if notif_layout:
			values['layout'] = notif_layout

		# 3. Attachments
		#   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
		attachment_ids = self._message_post_process_attachments(attachments, kwargs.pop('attachment_ids', []), values)
		values['attachment_ids'] = attachment_ids

		for x in ('from', 'to', 'cc'):
			values.pop(x, None)

		canned_response_ids = values.pop('canned_response_ids', False)
		new_message = MailMessage.create(values)
		values['canned_response_ids'] = canned_response_ids
		self._message_post_after_hook(new_message, values, model_description=model_description, mail_auto_delete=mail_auto_delete)
		return new_message

