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
{
    'name': 'Reconciliation in accounting Community',
    'version': '17.0.3.0.0',
    'category': 'Accounting',
    'summary': 'Regenerated feature in community that reconciles your invoice,vendor bills along with your bank statements',
    'description': 'Regenerated feature in community that reconciles your invoice,vendor bills along with your bank statements',
    'sequence': '1',
    'author': 'Harhu IT Solutions',
    'maintainer': 'Harhu IT Solutions',
    'contributors': ["Harhu IT Solutions"],
    'website': 'http://www.harhu.com',
    'live_test_url': 'https://www.harhu.com/contactus',
    'depends': ['account'],
    'demo': [],
    'data': [
        'views/account_view.xml',
        'views/account_bank_statement_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/account_payment_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'reconciliation/static/src/scss/reconciliation.scss',
            'reconciliation/static/src/js/reconciliation_action.js',
            'reconciliation/static/src/js/reconciliation_model.js',
            'reconciliation/static/src/js/reconciliation_renderer.js',
        ],
         'web.assets_qweb': [
            "reconciliation/static/src/xml/reconciliation.xml",
        ],
    },
    'license': 'OPL-1',
    'price': 50,
    'currency': 'USD',
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/poster_image.gif'],
}
