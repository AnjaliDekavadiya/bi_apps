# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import uuid
from markupsafe import Markup
from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT



class DirectoriesMain(models.Model):
	_name = "directorie.document"
	_description = "directorie model"


	name = fields.Char(string="Directory Name",required = True)
	parent_directory = fields.Many2one("directorie.document",string="Parent Directory")
	entry_sequence = fields.Many2one('ir.sequence',string="Entry Sequence",compute="genarate_entry")
	groups_ids = fields.One2many("security.group","document_id",string="Group")

	directory_code = fields.Char(string="Directory Code")
	model = fields.Many2one("ir.model",string="Model")

	document_count = fields.Integer(compute='_docum_count',string="Attachments")
	_sql_constraints = [ ('name_uniq', 'unique (model)', _('Directory for this module already created !')), ]

	@api.depends('name')
	def genarate_entry(self):
		self.entry_sequence = None
		if self.name:
			entry_seq = self.env['ir.sequence'].sudo().create({'name':self.name,
													'implementation':'standard',
													})
			self.entry_sequence = entry_seq



	def _docum_count(self):
		self.document_count = 0.0
		if self.model:
			for s_id in self:
				support_ids = self.env['ir.attachment'].search(['|',('directory_id','=',self.id),("res_model",'=',self.model.model),('directory_name','=',self.name)])
				s_id.document_count = len(support_ids)
		if not self.model:
			support_ids = self.env['ir.attachment'].search([("directory_id",'=',self.id)])
			self.document_count = len(support_ids)
		return

	def butoon_count_payslip(self):
		self.ensure_one()
		domain = []
		if self.model:
			domain=['|',('directory_id','=',self.id),("res_model",'=',self.model.model),('directory_name','=',self.name)]
		if not self.model:
			domain=[("directory_id",'=',self.id)]

		return {
			'name': 'Attachments',
			'type': 'ir.actions.act_window',
			'view_mode': 'kanban,tree,form',
			'res_model': 'ir.attachment',
			'domain': domain,
		}



class InheritAttachment(models.Model):
	_inherit = "ir.attachment"

	document_name = fields.Char(required=True,string='Name')
	directory_id = fields.Many2one("directorie.document", string="Directory")
	directory_name = fields.Char(string="Directory name", related="directory_id.name")

	@api.onchange('res_name','document_name')
	def onc_name(self):
		if self.res_name:
			self.name = self.res_name
		else:
			self.name = self.document_name

	@api.model_create_multi
	def create(self, vals_list):
		if vals_list:
			res_mod =vals_list[0].get('res_model')
			res_name = vals_list[0].get('name')
			res = super(InheritAttachment, self).create(vals_list)
			get_code = self.env['directorie.document'].search([])
			for i in get_code:
				if res_mod == i.model.model :
					sequence=self.env['ir.sequence'].get('ir.attachment')
					if i.directory_code:
						a=i.directory_code+sequence+res_name
					else:
						a=res_name
					res.write({'document_name':a,
								'directory_id':i.id})
			return res

	def action_attachment_send(self):

		self.ensure_one()
		template_id = self.env['ir.model.data']._xmlid_lookup('bi_document.email_template_edi')[1]
		compose_form_id = self.env['ir.model.data']._xmlid_lookup('mail.email_compose_message_wizard_form')[1]

		attachment = {
			'name': (self.name),
			'datas': self.datas,
			'res_model': 'ir.attachment',
			'type': 'binary'
		}

		id = self.create(attachment)
		
		ctx = {
			'default_model': 'ir.attachment',
			'default_res_ids': self.ids,
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True,
			'force_email': True,
		}

		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}
	


class InheritMessase(models.TransientModel):
	_inherit = "mail.compose.message"

	@api.model
	def default_get(self, fields_list):
		active_id = self._context.get('active_ids')
		compose_id = self.env['mail.compose.message'].browse(active_id)
		attachment_id = self.env['ir.attachment'].search([('id','=',compose_id.id)])
		res = super(InheritMessase, self).default_get(fields_list)
		if res.get('model') not in ['helpdesk.ticket',None]: 
			if res.get('res_ids') and res.get('model') and \
					res['composition_mode'] != 'mass_mail': 			
				res['attachment_ids'] = attachment_id			
		return res
	
	

	def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
				  email_layout_xmlid=False):
		""" Process the wizard content and proceed with sending the related
			email(s), rendering any template patterns on the fly if needed. """
		notif_layout = self._context.get('custom_layout')
		# Several custom layouts make use of the model description at rendering, e.g. in the
		# 'View <document>' button. Some models are used for different business concepts, such as
		# 'purchase.order' which is used for a RFQ and and PO. To avoid confusion, we must use a
		# different wording depending on the state of the object.
		# Therefore, we can set the description in the context from the beginning to avoid falling
		# back on the regular display_name retrieved in '_notify_prepare_template_context'.
		model_description = self._context.get('model_description')
		for wizard in self:
			# Duplicate attachments linked to the email.template.
			# Indeed, basic mail.compose.message wizard duplicates attachments in mass
			# mailing mode. But in 'single post' mode, attachments of an email template
			# also have to be duplicated to avoid changing their ownership.
			if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
				new_attachment_ids = []
				for attachment in wizard.attachment_ids:
					if not attachment.document_name:
						if attachment.name:
							attachment.document_name = attachment.name
					if attachment in wizard.template_id.attachment_ids:
						new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
					else:
						new_attachment_ids.append(attachment.id)
				new_attachment_ids.reverse()
				wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

			# Mass Mailing
			mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

			Mail = self.env['mail.mail']
			ActiveModel = self.env[wizard.model] if wizard.model and hasattr(self.env[wizard.model], 'message_post') else self.env['mail.thread']
			if wizard.composition_mode == 'mass_post':
				# do not send emails directly but use the queue instead
				# add context key to avoid subscribing the author
				ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
			# wizard works in batch mode: [res_id] or active_ids or active_domain
			if mass_mode and wizard.use_active_domain and wizard.model:
				res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
			elif mass_mode and wizard.model and self._context.get('active_ids'):
				res_ids = self._context['active_ids']
			else:
				res_ids = [wizard.res_id]

			batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
			sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

			if wizard.composition_mode == 'mass_mail' or wizard.is_log or (wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
				subtype_id = False
			elif wizard.subtype_id:
				subtype_id = wizard.subtype_id.id
			else:
				subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

			for res_ids in sliced_res_ids:
				batch_mails = Mail
				all_mail_values = wizard.get_mail_values(res_ids)
				for res_id, mail_values in all_mail_values.items():
					if wizard.composition_mode == 'mass_mail':
						batch_mails |= Mail.create(mail_values)
					else:
						post_params = dict(
							message_type=wizard.message_type,
							subtype_id=subtype_id,
							email_layout_xmlid=notif_layout,
							add_sign=not bool(wizard.template_id),
							mail_auto_delete=wizard.template_id.auto_delete if wizard.template_id else False,
							model_description=model_description)
						post_params.update(mail_values)
						if ActiveModel._name == 'mail.thread':
							if wizard.model:
								post_params['model'] = wizard.model
								post_params['res_id'] = res_id
							if not ActiveModel.message_notify(**post_params):
								# if message_notify returns an empty record set, no recipients where found.
								raise UserError(_("No recipient found."))
						else:
							ActiveModel.browse(res_id).message_post(**post_params)

				if wizard.composition_mode == 'mass_mail':
					batch_mails.send(auto_commit=auto_commit)

class group_list(models.Model):

	_name = "security.group"


	name = fields.Char("Name")
	code = fields.Text("Code")
	document_id = fields.Many2one("directorie.document",string="Documenentry")

