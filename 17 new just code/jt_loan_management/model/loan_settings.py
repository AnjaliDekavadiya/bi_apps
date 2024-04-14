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


from odoo import api, fields, models,_
from ast import literal_eval

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    write_off_account_id = fields.Many2one('account.account', string='Write-Off Account')
    principal_prod_id = fields.Many2one('product.product', string='Principal Product',
            help='Product used to invoice as principal of the loans.')
    interest_prod_id = fields.Many2one('product.product', string='Interest Product',
            help='Product used to invoice as interest of the loans.')
    processing_fee_prod_id = fields.Many2one('product.product', string='Processing Fee',
           help='Product used as Processing fee of the loans.')
    acc_rec_id = fields.Many2one('account.account', string="Loan Account Receivable")
    income_acc_id = fields.Many2one('account.account', string="Loan Income Account")
    loan_jou_id = fields.Many2one('account.journal', string="Loans Journal")
    disbursement_acc_id = fields.Many2one('account.account', string="Disbursement Account")
    disbursement_journal_id = fields.Many2one('account.journal',string="Disbursement Journal")
    inv_create_date = fields.Integer(string='No. of Days', help="Installment Invoice Create Date before how much days from installment due date.")

    penalty_option = fields.Selection([
        ('penalty', 'Penalty'),
        ('interest', 'Interest')],
        string="Penalty / Interest ?",
        default='penalty')

    charge_option = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage')],
        default='fixed',
        string="Due penalty method")

    charge = fields.Float(string="Charge", digits=(16, 2))
    of_days = fields.Integer(string="Allow # of days after due", default=2)

    @api.onchange('penalty_option')
    def onchange_penalty_option(self):
        if self.penalty_option == 'interest':
            self.charge_option = 'percentage'
        if not self.penalty_option:
            self.charge_option = False
            self.charge = 0.00
            self.of_days = 2
            
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        write_off_account_id = literal_eval(ICPSudo.get_param('jt_loan_management.write_off_account_id','False'))
        principal_prod_id = literal_eval(ICPSudo.get_param('jt_loan_management.principal_prod_id','False'))
        interest_prod_id = literal_eval(ICPSudo.get_param('jt_loan_management.interest_prod_id','False'))
        processing_fee_prod_id = literal_eval(ICPSudo.get_param('jt_loan_management.processing_fee_prod_id','False'))
        acc_rec_id = literal_eval(ICPSudo.get_param('jt_loan_management.acc_rec_id', 'False'))
        income_acc_id = literal_eval(ICPSudo.get_param('jt_loan_management.income_acc_id', 'False'))
        loan_jou_id = literal_eval(ICPSudo.get_param('jt_loan_management.loan_jou_id', 'False'))
        disbursement_acc_id = literal_eval(ICPSudo.get_param('jt_loan_management.disbursement_acc_id', 'False'))
        disbursement_journal_id = literal_eval(ICPSudo.get_param('jt_loan_management.disbursement_journal_id', 'False'))
        inv_create_date = int(ICPSudo.get_param('jt_loan_management.inv_create_date',0))
        penalty_option = ICPSudo.get_param(
            'jt_loan_management.penalty_option')
        charge_option = ICPSudo.get_param(
            'jt_loan_management.charge_option')
        charge = float(ICPSudo.get_param(
            'jt_loan_management.charge'))
        of_days = int(ICPSudo.get_param(
            'jt_loan_management.of_days'))

        res.update(
            write_off_account_id = write_off_account_id,
            principal_prod_id = principal_prod_id,
            interest_prod_id = interest_prod_id,
            processing_fee_prod_id = processing_fee_prod_id,
            acc_rec_id = acc_rec_id,
            income_acc_id = income_acc_id,
            loan_jou_id = loan_jou_id,
            disbursement_acc_id = disbursement_acc_id,
            disbursement_journal_id = disbursement_journal_id,
            inv_create_date = inv_create_date,
            penalty_option=penalty_option,
            charge_option=charge_option,
            charge=charge,
            of_days=of_days,
        )
        return res

    # @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("jt_loan_management.write_off_account_id", self.write_off_account_id.id)
        ICPSudo.set_param("jt_loan_management.principal_prod_id", self.principal_prod_id.id)
        ICPSudo.set_param("jt_loan_management.interest_prod_id", self.interest_prod_id.id)
        ICPSudo.set_param("jt_loan_management.processing_fee_prod_id", self.processing_fee_prod_id.id)
        ICPSudo.set_param("jt_loan_management.acc_rec_id", self.acc_rec_id.id)
        ICPSudo.set_param("jt_loan_management.income_acc_id", self.income_acc_id.id)
        ICPSudo.set_param("jt_loan_management.loan_jou_id", self.loan_jou_id.id)
        ICPSudo.set_param("jt_loan_management.disbursement_acc_id", self.disbursement_acc_id.id)
        ICPSudo.set_param("jt_loan_management.disbursement_journal_id", self.disbursement_journal_id.id)
        ICPSudo.set_param("jt_loan_management.inv_create_date", self.inv_create_date)

        charge_option = self.charge_option

        if self.penalty_option == 'interest':
            charge_option = 'percentage'

        ICPSudo.set_param(
            'jt_loan_management.penalty_option', self.penalty_option)
        ICPSudo.set_param(
            'jt_loan_management.charge_option', charge_option)
        ICPSudo.set_param('jt_loan_management.charge', self.charge)
        ICPSudo.set_param(
            'jt_loan_management.of_days', self.of_days or 2)