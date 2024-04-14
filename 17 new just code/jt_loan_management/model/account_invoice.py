# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models, _
from datetime import datetime
import logging
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF
from dateutil.relativedelta import *
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta as rd

_logger = logging.getLogger(__name__)

try:
    import numpy
except (ImportError, IOError) as err:
    _logger.error(err)

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    emi = fields.Boolean('Is Installment?')
    is_down_payment = fields.Boolean('Is Downpayment?')
    splitted_invoice = fields.Boolean("Splitted Invoice")
    main_invoice_id = fields.Many2one("account.move")
   
    penalty = fields.Boolean(string="Penalty?", copy=False)
    interest_inv_id = fields.Integer(string="Interest inv ref", copy=False)
    interest_due_date = fields.Date(string="Interest Due Date", copy=False)

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        res.update({'interest_due_date': res.invoice_date_due})
        return res


    @api.model
    def check_due_invoice(self):
        invoice_line_obj = self.env['account.move.line']
        current_date = datetime.strptime(str(fields.Date.context_today(self)), DF).date()
        domain = [('move_type', '=', 'out_invoice'),
                  ('state', '=', 'posted'),
                  ('payment_state', '!=', 'paid'),
                  ('penalty', '!=', True),
                  ('company_id.id','=',self.env.user.company_id.id)]

        # Checking penalty configuration
        IPC = self.env['ir.config_parameter'].sudo()
        penalty_option = IPC.get_param(
            'jt_loan_management.penalty_option')
        charge_option = IPC.get_param(
            'jt_loan_management.charge_option')
        charge = float(IPC.get_param(
            'jt_loan_management.charge'))
        of_days = int(IPC.get_param(
            'jt_loan_management.of_days'))

        if penalty_option == 'penalty':
            domain.append(('invoice_date_due', '<', current_date.today()))
        else:
            domain.append(('interest_due_date', '<', current_date.today()))

        invoice_ids = self.search(domain)
        _logger.info("Checking Due Invoices")
        

        try:
            if penalty_option:
                penalty_product_id = self.env.ref(
                    'jt_loan_management.product_product_penalty')
                interest_inv_id = False
                penalty = True
                name = 'Penalty of '
                line_vals = []

                if penalty_option == 'interest':
                    # penalty_product_id = self.env.ref(
                    #     'jt_loan_management.product_product_penalty')
                    penalty = False
                    name = 'Penalty Interest of '   
                for inv in invoice_ids:
                    due_date = inv.invoice_date_due
                    new_dt = due_date + rd(days=of_days)
                    if penalty_option == 'interest' and new_dt.month == current_date.month:
                        continue
                    if new_dt < current_date:
                        charge_amt = charge

                        if penalty_option == 'penalty' and \
                                charge_option == 'percentage':
                            charge_amt = charge_amt * inv.amount_residual / 100
                        elif penalty_option == 'interest':
                            charge_amt = charge_amt / 12 * \
                                inv.amount_residual / 100
                            interest_inv_id = inv.id
                        account = (penalty_product_id.property_account_income_id
                                   and penalty_product_id.property_account_income_id.id) \
                            or (penalty_product_id.categ_id.property_account_income_categ_id
                                and penalty_product_id.categ_id.property_account_income_categ_id.id)

                        interest_inv_id = self.search([('interest_inv_id', '=', inv.id),
                                                       ('payment_state', '=', 'not_paid')])
                        if penalty_option == 'interest' and interest_inv_id:

                            invoice_line_obj.create({
                                'invoice_id': interest_inv_id.id,
                                'product_id': penalty_product_id.id,
                                'name': name +
                                datetime.strftime(
                                    current_date.today(), '%B %Y'),
                                'quantity': 1,
                                'product_uom_id': penalty_product_id.uom_id.id,
                                'price_unit': charge_amt,
                                'account_id': account,
                                'tax_ids': []
                            })

                        else:
                            interest_due_date1 = datetime.strptime(
                                str(inv.interest_due_date), DF).date()
                            diff_months = relativedelta.relativedelta(
                                current_date, interest_due_date1)

                            if diff_months.months:
                                for diff in range(diff_months.months):
                                    line_vals.append((0, 0, {
                                        'product_id': penalty_product_id.id,
                                        'name': name +
                                                     datetime.strftime(
                                                         interest_due_date1, '%B %Y'),
                                                     'quantity': 1,
                                                     'product_uom_id': penalty_product_id.uom_id.id,
                                                     'price_unit': charge_amt,
                                                     'account_id': account,
                                                     'tax_ids': []}))
                                    interest_due_date1 = interest_due_date1 + \
                                        rd(months=1)
                            else:
                                line_vals.append((0, 0, {
                                                 'product_id': penalty_product_id.id,
                                                 'name': name +
                                                 datetime.strftime(
                                                     current_date.today(), '%B %Y'),
                                                 'quantity': 1,
                                                 'product_uom_id': penalty_product_id.uom_id.id,
                                                 'price_unit': charge_amt,
                                                 'account_id': account,
                                                 'tax_ids': [],
                                                 }))
                            inv.write({'invoice_line_ids':line_vals})
                            line_vals = []
                            inv.penalty = penalty
                        inv.interest_due_date = current_date
                        _logger.info(
                            "Penalty invoice created based on due date.")
            return True
        except:
            _logger.info("Please check due invoice penalty configuration !")

        def write(self, vals):
            result = super(AccountInvoice, self).write(vals)
            if 'date_due' in vals:
                for rec in self:
                    rec.interest_due_date = vals['invoice_date_due']


class PartnerInherit(models.Model):
    _inherit = 'res.partner'

    loan_count = fields.Integer(string='Loans', compute="get_loan_count")
    total_payment_amount = fields.Float('Total Payment Amount', compute='cal_payment_amt')

    # @api.multi
    def cal_payment_amt(self):
        """
        Calculate total payment amount of loan.
        :return:
        """
        pay_his_obj = self.env['account.payment.history']
        for partner in self:
            histories = pay_his_obj.search([('partner_id', '=', partner.id)])
            partner.total_payment_amount = sum(history.amount for history in histories)
    
    # # @api.multi
    def get_loan_count(self):
        """
        Count total loan of partner.
        :return:
        """
        loan = self.env['account.loan']
        for partner in self:
            partner.loan_count = len(loan.search([('partner_id', '=', partner.id)]))
