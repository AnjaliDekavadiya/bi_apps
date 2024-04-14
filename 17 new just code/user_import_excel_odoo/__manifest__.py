# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Import Users from Excel',
    'version': '5.1.22',
    'price': 9.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Human Resources',
    'summary':  """This module allow you to import Users and their images from excel using URL and Path.""",
    'description': """
This module gives allow you to create Users and modify existing users image on wizard.
import users
user import
users import
res.users
import user
Import Users from Excel
    """,
    'images': ['static/description/img.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/user_import_excel_odoo/864',#'https://youtu.be/nmSleCPPOAo',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/user_import.xml',
        'views/menu.xml',
    ],
    'installable' : True,
    'application' : True,
}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 

