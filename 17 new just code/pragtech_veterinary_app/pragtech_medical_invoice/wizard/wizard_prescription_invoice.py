from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime


class MedicalPrescriptionInvoice(models.TransientModel):
    _name = "medical.prescription.invoice"

    def create_prescription_invoice(self):
        result = {}
        pres_request_obj = self.env['medical.prescription.order']
        invoice_obj = self.env['account.move']
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        invoice_data = {}
        prods_lines = []
        inv_id_list = []
        partner_list = []
        for record in pres_request_obj.browse(active_ids):
            if record.name.id not in partner_list:
                partner_list.append(record.name.id)
        if len(partner_list) > 1:
            raise UserError(_('When multiple prescription are selected, patient must be the same.'))
        for record in pres_request_obj.browse(active_ids):
            if record.no_invoice:
                raise UserError(_('At least one of the selected prescription is invoice exempt.'))
            if record.invoice_status == 'invoiced':
                raise UserError(_('At least one of the selected prescription is already invoiced.'))
            if record.name.name.id:
                if record.name.name.property_account_receivable_id.id:
                    invoice_data['partner_id'] = record.name.name.id
                    invoice_data['account_id'] = record.name.name.property_account_receivable_id.id
                    invoice_data[
                        'fiscal_position_id'] = record.name.name.property_account_position_id and record.name.name.property_account_position_id.id or False
                    invoice_data[
                        'payment_term_id'] = record.name.name.property_payment_term_id and record.name.name.property_payment_term_id.id or False
                else:
                    raise UserError(_('Account is not added for Patient.'))
            if record.prescription_line:
                for pres_line in record.prescription_line:
                    account_id = pres_line.medicament.name.product_tmpl_id.property_account_income_id.id
                    if not account_id:
                        account_id = pres_line.medicament.name.categ_id.property_account_income_categ_id.id
                    if not account_id:
                        raise UserError(_('Account is not added for test.'))
                    prods_lines.append((0, 0, {'product_id': pres_line.medicament.name.id,
                                               'name': pres_line.medicament.name.name,
                                               'quantity': pres_line.quantity,
                                               'account_id': account_id,
                                               'price_unit': pres_line.medicament.name.lst_price}))

            else:
                raise osv.except_osv(_('UserError'),
                                     _('You need to have at least one prescription item in your invoice'))

        invoice_data['invoice_line_ids'] = prods_lines
        invoice_id = invoice_obj.create(invoice_data)
        inv_id_list.append(invoice_id.id)
        for record in pres_request_obj.browse(active_ids):
            record.write({'inv_id': invoice_id.id, 'invoice_status': 'invoiced'})

        imd = self.env['ir.model.data']
        res_id = imd._xmlid_to_res_id('account.invoice_tree')
        res_id_form = imd._xmlid_to_res_id('account.invoice_form')
        result = {
            'name': 'Create invoice',
            'type': 'tree',
            'views': [(res_id, 'tree'), (res_id_form, 'form')],
            'target': 'current',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        if inv_id_list:
            result['domain'] = "[('id','in',%s)]" % inv_id_list
            result['res_id'] = inv_id_list[0]
        return result
