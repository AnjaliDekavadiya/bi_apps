# # -*- coding: utf-8 -*-

# import time
# from odoo import api, models

# class AccountPaymentReport(models.AbstractModel):
#     _name = "report.website_portal_payments.print_payment_report_web"
  
#     @api.model
#     def render_html(self, docids, data=None):
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': 'account.payment',
#             'data': data,
#             'docs': self.env['account.payment'].sudo().browse(docids),
#         }
#         return self.env['report'].sudo().render('website_portal_payments.print_payment_report_web', docargs)
