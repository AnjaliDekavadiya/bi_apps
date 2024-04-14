# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': "Import Daily Currency Rates",
    'version': '6.2.1',
    'category': 'Accounting & Finance',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow you to Import Daily Currency Rate from excel.""",
    'description':  """
Odoo Import Daily Currency Rate
currency import
currency rate import
import currency rates
daily rate
daily currency rates
               """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/import_daily_currency_rates/968',#'https://youtu.be/BT6EieoyvIk',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_daily_currency_rates_view.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
