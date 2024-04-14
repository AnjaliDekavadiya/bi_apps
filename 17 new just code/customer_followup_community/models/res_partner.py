# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Gokul P I (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (
#    OPL-1) It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
from odoo import fields, models


class CustomerFollowPartner(models.Model):
    """This class extends the 'res.partner' model to add custom fields and
     functionality related to customer follow-up."""
    _inherit = 'res.partner'

    invoice_ids = fields.One2many('account.move', 'partner_id',
                                  string="Invoice Details",
                                  help='Corresponding invoice details',
                                  readonly=True,
                                  domain=([('payment_state', '=', 'not_paid'),
                                           ('move_type', '=', 'out_invoice'),
                                           ('state', '=', 'posted')]))
    customer_followup_done_ids = fields.Many2one('followup.line',
                                                 string='Action Taken',
                                                 help='Action taken')
    customer_followup_to_do_ids = fields.Many2one('followup.line',
                                                  string='Next Action',
                                                  help='Next Action')
    next_followup_action_date = fields.Char(string='Next Action Date',
                                            help='Date for the next action')

    def get_min_date(self):
        """Get the minimum invoice due date among the partner's invoices."""
        for this in self:
            if this.invoice_ids:
                min_list = this.invoice_ids.mapped('invoice_date_due')
                return min(min_list)

    def action_send_invoice_mail(self):
        """Open a new window to compose an email with a predefined template
            for sending invoices to the partner."""
        template = self.env.ref(
            'customer_followup_community.mail_template_data_follow_cust_test')
        ctx = {
            'default_model': 'res.partner',
            'default_template_id': template.id,
            'default_partner_ids': [self.id],
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    def action_print_followup_letter(self):
        """Print the follow-up letter for the partner."""
        return self.env.ref(
            'customer_followup_community.action_report_followup_community').report_action(
            self, data='')
