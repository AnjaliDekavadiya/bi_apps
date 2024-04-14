# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Journal Entries Import - Multiple',
    'version': '6.4.1',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to import multiple journal entries from excel file.""",
    'description': """
Odoo Multiple Journal Entry Import.
This module import journal entries from excel file
Journal Entry Import from Excel
Import Journal Items
Import Items
Import journal
journal entry import
import journal
import journal entry odoo
import journal items
journal items import
journal import
journal entries import
import journal entries
opening entry import
opening balance import
partner balance import
journal entry excel import
journal items excel import
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/multiple_journal_entry_import/908',#'https://youtu.be/Oe8R3Ne2kXI',
    'category': 'Accounting',
    'depends': [
                'account',
                ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/import_excel_wizard.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
