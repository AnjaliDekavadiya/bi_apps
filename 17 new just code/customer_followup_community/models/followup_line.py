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
from odoo import api, fields, models


class FollowupLine(models.Model):
    """This class extends the 'followup.line' model to add custom fields and
    functionality related to follow-up lines."""
    _inherit = 'followup.line'
    _description = 'Followup Line'
    _order = 'delay'

    after_before = fields.Selection([('after', 'After'),
                                     ('before', 'Before')],
                                    default='after',
                                    help='Option to send remainder '
                                         'after/before due days')
    days_hours = fields.Selection([('days', 'Days'),
                                   ('hours', 'Hours')],
                                  default='days', help='Option to set '
                                                       'remainder mail for '
                                                       'days/hours ')

    @api.onchange('after_before', 'delay')
    def _onchange_selection(self):
        """This method is triggered when the 'after_before' or 'delay' fields
        are changed.It adjusts the 'delay' field based on the 'after_before'
        selection."""
        if self.after_before:
            if self.after_before == 'after':
                self.delay = abs(self.delay)
            else:
                self.delay = -1 * abs(self.delay)

    description_after = fields.Html('Printed Message', translate=True,
                                    default="""
        Dear Sir/Madam,
        Exception made if there was a mistake of ours, it seems that the 
        following amount stays unpaid. Please, take appropriate measures in 
        order to carry out this payment in the next 8 days.Would your payment 
        have been carried out after this mail was sent, please ignore this 
        message. Do not hesitate to contact our accounting department.
        Best Regards,""")
    description_before = fields.Html('Message', translate=True,
                                     default="""
            Dear Sir/Madam,
            This mail is with regard to the following amount that stays unpaid 
            from your end.Kindly, make the payment on or before the due date.
            In case, if your payment has already been carried out meanwhile 
            this time, please ignore this message.
            Do not hesitate to contact our accounting department. 
            Best Regards,""")
    send_email = fields.Boolean(string='Send an Email',
                                help="When processing, it will send an email",
                                default=True)
    print_letter = fields.Boolean(string='Print a Letter',
                                  help="When processing, it will print a PDF",
                                  default=True)
    _sql_constraints = [('days_uniq', 'unique(followup_id, delay)',
                         'Days of the follow-up levels must be different')]
