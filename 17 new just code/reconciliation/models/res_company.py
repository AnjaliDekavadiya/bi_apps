# -*- coding: utf-8 -*-
###################################################################################
#
#    Harhu IT Solutions
#    Copyright (C) 2019-TODAY Harhu IT Solutions (http://harhutech.com).
#    Author: Harhu IT Solutions (http://harhutech.com)
#
#    you can modify it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#
###################################################################################
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_bank_reconciliation_start = fields.Date(string="Bank Reconciliation Threshold",
                                                    help="""The bank reconciliation widget won't ask to reconcile
                                                     payments older than this date. This is useful if you install 
                                                     accounting after having used invoicing for some time and don't 
                                                     want to reconcile all the past payments with bank statements.""")
