# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    so_three_step_validation =  fields.Boolean(
        'Three Step Approval',
        related='company_id.so_three_step_validation',
        readonly=False,
    )
    so_double_validation = fields.Selection(
        [('one_step','Confirm Sale Order in One Step'),
         ('two_step','Get 2 Level Approvals to Confirm a Sale Order')],
        default='one_step',
        related='company_id.so_double_validation',
        readonly=False,
        string='Level of SO Approvals'
    )
    so_finance_validation_amount = fields.Monetary(
        'Finance Validation Amount',
        # default=0.0,
        related='company_id.so_finance_validation_amount',
        readonly=False,
        # currency_field='company_currency_id',
    )
    so_double_validation_amount = fields.Monetary(
        'SO Double Validation Amount',
        # default=0.0,
        related='company_id.so_double_validation_amount',
        readonly=False,
        # currency_field='company_currency_id',
    )
    so_director_validation_amount = fields.Monetary(
        'Director Validation Amount',
        # default=0.0,
        related='company_id.so_director_validation_amount',
        readonly=False,
        # currency_field='company_currency_id',   
    )
    so_email_template_id = fields.Many2one(
        'mail.template',
        string='Sale Approval Email Template',
        config_parameter='sale_tripple_approval.so_email_template_id',
    )
    so_refuse_template_id = fields.Many2one(
        'mail.template',
        string='Sale Refuse Email Template',
        config_parameter='sale_tripple_approval.so_refuse_template_id',
    )

    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     res['so_three_step_validation'] = self.env['ir.config_parameter'].sudo().get_param('sale_tripple_approval.so_three_step_validation', self.so_three_step_validation)
    #     res['so_double_validation_amount'] = self.env['ir.config_parameter'].sudo().get_param('sale_tripple_approval.so_double_validation_amount', self.so_double_validation_amount)
    #     res['so_finance_validation_amount'] = self.env['ir.config_parameter'].sudo().get_param('sale_tripple_approval.so_finance_validation_amount', self.so_finance_validation_amount)
    #     res['so_director_validation_amount'] = self.env['ir.config_parameter'].sudo().get_param('sale_tripple_approval.so_director_validation_amount', self.so_director_validation_amount)
    #     return res

    # #@api.model
    # def set_values(self):
    #        self.env['ir.config_parameter'].sudo().set_param('sale_tripple_approval.so_three_step_validation', self.so_three_step_validation)
    #        self.env['ir.config_parameter'].sudo().set_param('sale_tripple_approval.so_double_validation_amount', self.so_double_validation_amount)
    #        self.env['ir.config_parameter'].sudo().set_param('sale_tripple_approval.so_finance_validation_amount', self.so_finance_validation_amount)
    #        self.env['ir.config_parameter'].sudo().set_param('sale_tripple_approval.so_director_validation_amount', self.so_director_validation_amount)
    #     super(ResConfigSettings, self).set_values()

# 
#     @api.model
#     def get_values(self):
#         res = super(SaleConfigSettings, self).get_values()
#         params = self.env['ir.config_parameter'].sudo()
#         res.update(
#             so_three_step_validation = params.get_param('sale_tripple_approval.so_three_step_validation'),
# #             finance_validation_amount = params.get_param('purchase_tripple_approval.finance_validation_amount'),
# #             director_validation_amount = params.get_param('purchase_tripple_approval.director_validation_amount'),
# #             email_template_id = params.get_param('purchase_tripple_approval.email_template_id'),
# #             refuse_template_id = params.get_param('purchase_tripple_approval.refuse_template_id')
#         )
#         if self.so_email_template_id:
#             res.update(
#             email_template_id = params.get_param('sale_tripple_approval.so_email_template_id'),
#         )
#         return res
# 
#     @api.multi
#     def set_values(self):
#         super(SaleConfigSettings, self).set_values()
#         ICPSudo = self.env['ir.config_parameter'].sudo()
#         ICPSudo.set_param("sale_tripple_approval.so_three_step_validation", self.so_three_step_validation)
# #         ICPSudo.set_param("purchase_tripple_approval.finance_validation_amount", self.finance_validation_amount)
# #         ICPSudo.set_param("purchase_tripple_approval.director_validation_amount", self.director_validation_amount)
#         if self.so_email_template_id:
#             ICPSudo.set_param("sale_tripple_approval.so_email_template_id", self.so_email_template_id)
# #       
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
