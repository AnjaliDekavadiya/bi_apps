# coding: utf-8

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'
    
#     @api.model
#     def create(self, vals):
#         payment_acquire = self.env['payment.acquirer'].search([('provider','=','cod')], limit=1)
#         if payment_acquire:
#             vals.update({
#                 'payment_acquire_id': payment_acquire.id
#                 })
#         return super(Partner, self).create(vals)
    
    @api.model
    def _get_cod_payment_method(self):
#        payment_acquire = self.env['payment.acquirer'].search([('provider','=','cod')], limit=1)
        payment_acquire = self.env['payment.provider'].search([('code','=','cod')], limit=1)
        return payment_acquire
    
    cod_payment_acquire_id = fields.Many2one(
#        'payment.acquirer',
        'payment.provider',
        string='Payment Acquiers',
        copy=True,
        default=_get_cod_payment_method
    )
    
    @api.depends('cod_payment_acquire_id', 'state_id', 'country_id',  'zip',
#                 'cod_payment_acquire_id.country_ids',
                'cod_payment_acquire_id.available_country_ids',
                 'cod_payment_acquire_id.cod_state_ids',
                 'cod_payment_acquire_id.cod_zip_code_ids')
    def _compute_is_cod_applicable(self):
        cod = self.env['payment.provider'].search([('code', '=', 'cod')])
        zip_name = []
        for zipcode in cod.cod_zip_code_ids:
            zip_name.append(zipcode.name)

        for rec in self:
            if not rec.cod_payment_acquire_id:
                rec.is_cod_applicable = False
                continue

            rec.is_cod_applicable = True

            if rec.is_cod_applicable:
                # check for country
                if cod.available_country_ids:
                    if not rec.country_id:
                        rec.is_cod_applicable = False
                    elif rec.country_id.id not in cod.available_country_ids.ids:
                        rec.is_cod_applicable = False
                    
            if rec.is_cod_applicable:
                # check for state
                if cod.cod_state_ids:
                    if not rec.state_id:
                        rec.is_cod_applicable = False
                    elif rec.state_id.id not in cod.cod_state_ids.ids:
                        rec.is_cod_applicable = False

            if rec.is_cod_applicable:
                # check for zip
                if zip_name:
                    if not rec.zip:
                        rec.is_cod_applicable = False
                    elif rec.zip not in zip_name:
                        rec.is_cod_applicable = False

#             rec.is_cod_applicable = False
#             if rec.country_id and rec.payment_acquire_id and rec.payment_acquire_id.country_ids:
#                 if rec.country_id.id in rec.payment_acquire_id.country_ids.ids:
#                     rec.is_cod_applicable = True
#             elif rec.country_id and rec.payment_acquire_id and not rec.payment_acquire_id.country_ids:
#                 rec.is_cod_applicable = True
# 
#             if rec.state_id and rec.payment_acquire_id and rec.payment_acquire_id.state_ids:
#                 if rec.state_id.id in rec.payment_acquire_id.state_ids.ids:
#                     rec.is_cod_applicable = True
#             elif rec.state_id and rec.payment_acquire_id and not rec.payment_acquire_id.state_ids:
#                 rec.is_cod_applicable = True
#             
#             if rec.zip and rec.payment_acquire_id and rec.payment_acquire_id.zip_code_ids:
#                 for z in rec.payment_acquire_id.zip_code_ids:
#                     if rec.zip == z.name:
#                         rec.is_cod_applicable = True
#             if rec.zip and rec.payment_acquire_id and not rec.payment_acquire_id.zip_code_ids:
#                 rec.is_cod_applicable = True
    
    is_cod_applicable = fields.Boolean(
        string='COD Applicable?',
        compute='_compute_is_cod_applicable',
    )
    
