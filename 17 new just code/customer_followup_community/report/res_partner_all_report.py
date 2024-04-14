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
from datetime import date
from odoo import api, models


class CustomerFollowupCommunityPrintAll(models.AbstractModel):
    """Abstract model for the follow-up community print all report."""
    _name = 'report.customer_followup_community.report'

    @api.model
    def _get_report_values(self, docids, data):
        """Get the values for the follow-up community print all report.
                :param docids: The document ids.
                :param data: Additional data.
                :return: Dictionary containing report values."""
        partner_ids = [line.id for line in self.env['res.partner'].search([])
                       if
                       line.invoice_ids.filtered(
                           (lambda t: t.partner_id.id == line.id))]
        return {
            'today': date.today(),
            'partner': self.env['res.partner'].browse(partner_ids)
        }
