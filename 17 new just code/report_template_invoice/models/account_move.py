# -*- coding: utf-8 -*-
from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_customer_invoice_template_id(self):
        self.ensure_one()
        if self.move_type not in ('out_invoice', 'out_refund'):
            return False
        return self.env['report.template'].sudo().get_template('report_customer_invoice', company_id=self.company_id)

    def get_report_customer_invoice_data(self, template):
        self.ensure_one()
        data = template.get_report_data_standard(template=template, rec=self)

        data['heading_name'] = {
            'draft': template.get_option_data('state_draft'),
            'posted': template.get_option_data('state_posted'),
            'cancel': template.get_option_data('state_cancel')
        }[self.state]

        return data

