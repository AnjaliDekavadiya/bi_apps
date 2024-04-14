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
from datetime import date, timedelta
from odoo import fields, models


class CustomerFollowWizard(models.TransientModel):
    """This transient model defines a wizard for handling customer
    follow-up actions."""
    _name = 'followup.mails'

    email_count_value = fields.Char(string='Email Count',
                                    help='Corresponding email count value')

    def get_delay(self):
        """Get the delay for the follow-up action from the database."""
        delay = """select id,delay from followup_line where followup_id =
        (select id from account_followup where company_id = %s)
         order by delay LIMIT 1"""
        self._cr.execute(delay, [self.env.user.company_id.id])
        record = self.env.cr.dictfetchall()
        return record

    def followp_wizard(self):
        """Open the wizard window for sending overdue emails."""
        return {
            'name': 'Send Overdue Emails',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'followup.mails',
            'target': 'new',
        }

    def action_send_followup_mail(self):
        """Send follow-up emails to partners with overdue invoices."""
        count = 0
        lines = self.env['followup.line'].search([(
            'followup_id.company_id', '=', self.env.user.company_id.id)])
        if lines:
            for partner in self.env['res.partner'].search(
                    [('invoice_ids', '!=', False)]):
                if partner.invoice_ids:
                    if not partner.customer_followup_to_do_ids and partner.customer_followup_done_ids:
                        continue
                    else:
                        if not partner.customer_followup_to_do_ids:
                            record = self.get_delay()
                            partner.customer_followup_to_do_ids = self.env[
                                'followup.line'].browse(record[0]['id'])
                            if partner.customer_followup_to_do_ids.days_hours == 'days':
                                date_min = partner.get_min_date() + timedelta(
                                    days=partner.customer_followup_to_do_ids.delay)
                            else:
                                date_min = partner.get_min_date() + timedelta(
                                    hours=partner.customer_followup_to_do_ids.delay)
                            partner.next_followup_action_date = \
                                str(date_min).split()[0]
                        date_min = partner.next_followup_action_date
                        action_date = date.today()
                        if str(action_date) >= str(date_min):
                            # followup date
                            list = lines.mapped('delay')
                            partner.customer_followup_done_ids = partner.customer_followup_to_do_ids
                            # next action date
                            if len(list) > list.index(
                                    partner.customer_followup_done_ids.delay) + 1:
                                next_delay = list[list.index(
                                    partner.customer_followup_done_ids.delay) + 1]
                                next_id = self.env['followup.line'].search(
                                    [('delay', '=', next_delay), (
                                        'followup_id.company_id', '=',
                                        self.env.user.company_id.id)]).id
                                partner.customer_followup_to_do_ids = self.env[
                                    'followup.line'].browse(next_id)
                                if partner.customer_followup_to_do_ids.days_hours == 'days':
                                    date_min = partner.get_min_date() + timedelta(
                                        days=partner.customer_followup_to_do_ids.delay)
                                else:
                                    date_min = partner.get_min_date() + timedelta(
                                        hours=partner.customer_followup_to_do_ids.delay)
                                partner.next_followup_action_date = \
                                    str(date_min).split()[0]
                            else:
                                # action completed
                                partner.customer_followup_to_do_ids = False
                                partner.next_followup_action_date = False
                            if partner.customer_followup_done_ids.after_before == 'before':
                                template = self.env.ref(
                                    'customer_followup_community.before_due_date_mail_template_followup')
                            else:
                                template = self.env.ref(
                                    'customer_followup_community.after_due_date_mail_template_followup')
                            self.env['mail.template'].browse(
                                template.id).sudo().send_mail(partner.id)
                            count += 1
                else:
                    partner.next_followup_action_date = False
                    partner.customer_followup_to_do_ids = False
                    partner.customer_followup_done_ids = False
        self.email_count_value = count
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'followup.mails',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_print_all_letter(self):
        """Print follow-up letters for all partners."""
        return self.env.ref(
            'customer_followup_community.action_report').report_action(self,
                                                                       data='')
