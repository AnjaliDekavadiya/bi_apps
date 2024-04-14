# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class MedicalAppointmentInvoice(models.TransientModel):
	_name = "medical.appointment.invoice"
	
	def create_invoice(self):
		result = {}
		appointment_obj = self.env['medical.appointment']
		invoice_obj = self.env['account.move']
		context = dict(self._context or {})
		active_ids = context.get('active_ids', []) or []
		partner_list = []
		for record in appointment_obj.browse(active_ids):
			if record.patient.id not in partner_list:
				partner_list.append(record.patient.id)
		if len(partner_list) > 1:
			raise UserError(_('When multiple lab tests are selected, patient must be the same.'))
		invoice_data = {}
		prods_lines = []
		inv_id_list = []
		for appointment in appointment_obj.browse(active_ids):
			if appointment.state == 'draft':
				raise UserError(_('At least one of the selected appointments is in Draft State. First Confirm it.'))
			if appointment.no_invoice:
				raise UserError(_('At least one of the selected appointments is invoice exempt.'))
			if appointment.validity_status == 'invoiced':
				raise UserError(_('At least one of the selected appointments is already invoiced.'))
			if appointment.patient.partner_id.id:
				if appointment.patient.partner_id.property_account_receivable_id.id:
					invoice_data['partner_id'] = appointment.patient.partner_id.id
					invoice_data['account_id'] = appointment.patient.partner_id.property_account_receivable_id.id
					invoice_data['fiscal_position_id'] = appointment.patient.partner_id.property_account_position_id and appointment.patient.partner_id.property_account_position_id.id or False
					invoice_data['payment_term_id'] = appointment.patient.partner_id.property_payment_term_id and appointment.patient.partner_id.property_payment_term_id.id or False
				else:
					raise UserError(_('Account is not added for Patient.'))
			if appointment.consultations:
				account_id = appointment.consultations.product_tmpl_id.property_account_income_id.id
				if not account_id:
					account_id = appointment.consultations.categ_id.property_account_income_categ_id.id
				if not account_id:
					raise UserError(_('Account is not added for set for Consultation.'))
				prods_lines.append((0, 0, {
					'product_id': appointment.consultations.id,
					'name': appointment.consultations.name,
					'quantity': 1,
					'account_id': account_id,
					'price_unit': appointment.consultations.lst_price
				}))
		invoice_data['invoice_line_ids'] = prods_lines
		invoice_id = invoice_obj.create(invoice_data)
		inv_id_list.append(invoice_id.id)
		for appointment in appointment_obj.browse(active_ids):
			appointment.write({'inv_id': invoice_id.id, 'validity_status': 'invoiced'})
		imd = self.env['ir.model.data']
		res_id = imd._xmlid_to_res_id('invoice_tree')
		res_id_form = imd._xmlid_to_res_id('invoice_form')
		result = {
			'name': 'Create invoice',
			'type': 'tree',
			'views': [(res_id, 'tree'),(res_id_form, 'form')],
			'target': 'current',
			'res_model': 'account.move',
			'type': 'ir.actions.act_window',
		}
		if inv_id_list:
			result['domain'] = "[('id','in',%s)]" % inv_id_list
			result['res_id'] = inv_id_list[0]
			
		return result
