# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import base64

class TransmittalSubmittal(models.Model):
	_name = 'transmittal.submittal'
	_description = "transmittals Submittals"

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			sequence_one=self.env['ir.sequence'].next_by_code('transmittal')
			sequence_two=self.env['ir.sequence'].next_by_code('submittal')
			if vals.get('document_type') == 'transmittal':
				vals['sequence'] = sequence_one
			else:
				vals['sequence'] = sequence_two
		res = super(TransmittalSubmittal,self).create(vals_list)
		return res

	name = fields.Char(string="Name",required=True)
	sequence = fields.Char(string='Number', readonly=True)
	project_id = fields.Many2one('project.project',string='Project')
	send_date = fields.Datetime(string="Date of Sending",default=datetime.today())
	account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
	end_date = fields.Datetime(string="Deadline")
	job_order_id = fields.Many2one('job.order','Job Order')
	job_cost_sheet_id = fields.Many2one('job.cost.sheet',string="Job Cost Sheet")
	document_type = fields.Selection([('transmittal','Transmittals'),('submittal','Submittals')],string="Document Type")
	user_id = fields.Many2one('res.users',string='Responsible User')
	sender_company = fields.Many2one('res.company', string='Sender Company')
	reciver_company = fields.Many2one('res.company', string='Receiver Company')
	submital_type = fields.Many2one('transmittal.submittal.type', string='Type')
	transmittal_line = fields.One2many('transmittal.submittal.orderline','transmittal_id',string="Transmital Lines")
	reason_of_sending = fields.Text(string="Reason of Sending")
	descriptin_by_recipient = fields.Text(string="Descriptin by Recipient")
	state = fields.Selection([
		('new', 'New'),
		('confirmed', 'Confirmed'),
		('approved', 'Approved'),
		('sent', 'Sent'),
		('refused','Refused'),
		], string='State', default='new')

	@api.onchange('end_date')
	def _onchange_deadline(self):
		if self.end_date and self.send_date:
			if self.send_date > self.end_date:
				raise UserError(_("Please select a proper date."))

	def action_confirm(self):
		self.write({'state':'confirmed'})
		return

	def action_approved(self):
		self.write({'state':'approved'})
		return
	
	def action_sent(self):
		self.write({'state':'sent'})
		return
		
	def action_refused(self):
		self.write({'state':'refused'})
		return

	def action_send_transmittal_email(self):
		template_id =  self.env['ir.model.data']._xmlid_lookup('bi_transmittals_submittals_communication.email_template_edi_transmittal')[1]

		template_browse = self.env['mail.template'].browse(template_id)
		if template_browse:
			values = template_browse._generate_template(self.ids, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
			for res_id, values in values.items():
				values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email
				values['email_to'] = self.user_id.email
				values['res_id'] = False
				values['subject'] = self.name +" "+ "("+self.sequence +")"
				values['author_id'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id
				if not values['email_to'] and not values['email_from']:
					pass
				ref = self.env.ref('bi_transmittals_submittals_communication.action_transmittal_submittal_report')
				pdf = self.env.ref('bi_transmittals_submittals_communication.action_transmittal_submittal_report')._render(report_ref=ref,res_ids=self.id)[0]
				values['attachment_ids'] = [(0,0,{
									'name': 'Transmittal/Submittal',
									'datas': base64.b64encode(pdf),
									'res_model': self._name,
									'res_id': self.id,
									'mimetype': 'application/x-pdf',
									'type': 'binary',
									})]
				mail_mail_obj = self.env['mail.mail']
				msg_id = mail_mail_obj.sudo().create(values)
				if msg_id:
					mail_mail_obj.sudo().send(msg_id)
		return True

class TransmittalSubmittalOrderline(models.Model):
	_name = 'transmittal.submittal.orderline'
	_description = "transmittals Orderline"

	transmittal_id = fields.Many2one('transmittal.submittal',string="Transmital")
	name = fields.Char(string="Name",required=True)
	description = fields.Char(string="Description")
	transmital_type = fields.Many2one('transmittal.submittal.type',string="Type")
	transmital_medium = fields.Many2one('transmittal.submittal.medium',string="Medium")

class MailTemplate(models.Model):
	_inherit = 'mail.template'

	def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
		res = super(MailTemplate, self).send_mail(res_id, force_send=False, raise_exception=False, email_values=None)
		if self._context.get('email_from') or self._context.get('email_to'):
			self.env['mail.mail'].sudo().browse(res).email_from = self._context.get('email_from')
			self.env['mail.mail'].sudo().browse(res).email_to = self._context.get('email_to')
			self.env['mail.mail'].sudo().browse(res).author_id = self.env['res.users'].browse(self._context.get('uid')).partner_id
