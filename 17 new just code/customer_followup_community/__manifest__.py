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
{
    'name': "Customer Followup",
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Implements Customer accounting followups for late payment',
    'description': 'The application will generate mail for each customer who '
                   'got with unpaid invoices.One can view the unpaid invoices '
                   'in the partner form. And thereby easily print it as a '
                   'letter or send as a mail to the customer enclosing the '
                   'invoice details.',
    'author': "Cybrosys Techno Solutions",
    'company': "Cybrosys Techno Solutions",
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base_accounting_kit'],
    'data': [
        'data/res_partner_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'report/res_partner_all_templates.xml',
        'report/res_partner_templates.xml',
        'report/res_partner_reports.xml',
        'views/followup_line.xml',
        'views/res_partner_views.xml',
        'views/followup_mails_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 29,
    'currency': 'EUR',
    'live_test_url': 'https://www.youtube.com/watch?v=rPoT1ZKceq0&feature=youtu.be',
}
