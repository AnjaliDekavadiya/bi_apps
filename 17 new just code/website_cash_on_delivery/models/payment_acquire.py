# coding: utf-8

from odoo import api, fields, models


class PaymentAcquire(models.Model):
#    _inherit = 'payment.acquirer'
    _inherit = 'payment.provider'

    not_allow_cod_product_ids = fields.Many2many(
        'product.product',
        string='Not Allowed Products',
    )
#    provider = fields.Selection(
#        selection_add=[('cod', 'Cash on Delivery')],
#        ondelete={'cod': 'set default'},
#    )
    code = fields.Selection(
        selection_add=[('cod', 'Cash on Delivery')],
        ondelete={'cod': 'set default'},
    )
    
    cod_min_order_amount = fields.Float(
        string='Minimum Order Amount',
    )
    cod_max_order_amount = fields.Float(
        string='Maximum Order Amount',
    )
#     country_ids = fields.Many2many(
#         'res.country',
#         string='Country',
#     )
    cod_state_ids = fields.Many2many(
        'res.country.state',
        string='State',
    )
#     zip_code = fields.Text(
#         string='Zip',
#     )
    cod_zip_code_ids = fields.One2many(
        'cod.zip.code',
        'payment_acquirer_id',
        string='Zip Code',
    )

    def cod_get_form_action_url(self):
        return '/payment/cod/feedback'

    # @api.multi #odoo13
    def write(self,vals):
        res = super(PaymentAcquire, self).write(vals)
        for rec in self:
            self.not_allow_cod_product_ids.write({'not_allow_cod' : True})
            domain = [
                ('not_allow_cod', '=', True),
                ('id', 'not in', self.not_allow_cod_product_ids.ids)
            ]
            allowed_product = self.env['product.product'].search(domain)
            allowed_product.write({'not_allow_cod': False})
        return res
# 
#     @api.multi
#     def cod_form_generate_values(self, values):
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         return values


    # @api.model
#    def _get_compatible_acquirers(
#        self, company_id, partner_id, currency_id=None, force_tokenization=False,
#        is_validation=False, **kwargs
#    ):
    @api.model
    def _get_compatible_providers(
        self, company_id, partner_id, amount, currency_id=None, force_tokenization=False,
        is_express_checkout=False, is_validation=False, **kwargs
    ):
#        acquires = super(PaymentAcquire, self)._get_compatible_acquirers(company_id=company_id, partner_id=partner_id, currency_id=currency_id, force_tokenization=force_tokenization, is_validation=is_validation, kwargs=kwargs)
        acquires = super(PaymentAcquire, self)._get_compatible_providers(company_id=company_id, partner_id=partner_id, amount=amount, currency_id=currency_id, force_tokenization=force_tokenization, is_express_checkout=is_express_checkout, is_validation=is_validation, kwargs=kwargs)
        if kwargs.get('sale_order_id'):
            sale_order = self.env['sale.order'].browse(int(kwargs.get('sale_order_id')))
            if not sale_order.is_cod:
                acquires = acquires.filtered(lambda acq:acq.code != 'cod')
        return acquires
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
