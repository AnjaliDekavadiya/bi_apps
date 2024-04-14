# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full
# copyright and licensing details.
{
    'name': 'CRM Leads Import from Excel File',
    'version': '3.2.5',
    'license': 'Other proprietary',
    'price': 25.0,
    'currency': 'EUR',
    'summary': 'Leads import from excel files in Odoo.',
    'description': """

This module will import Leads from .xls or .xlsx file (Excel files).
    Import Leads from excel
    Leads Import
    Import CRM Leads
    prospect import
    crm lead import
    lead import
    leads import
    oppotunity import
    pipeline import
    crm import
    excel import
    Odoo import
    sales card import
    sales history import
    crm_lead import
    crm_lead_import
    import leads from excel
    import leads from xls
    import lead from excel
    import lead from xls
    lead import using excel
This module will import Leads record/data from Excel - .xls or .xlsx file
supported

You have to install xlrd python package on your server/machine to use this
module.

Menu: Sales/Import/Import Leads

    """,

    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/crm_lead_import_excel/652',#'https://youtu.be/iL8VBze7S2A',
    'category': 'Sales',
    'depends': ['sale', 'crm', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/crm_import_excel.xml',
        'views/crm_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
