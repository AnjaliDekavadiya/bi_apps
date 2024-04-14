# -*- coding:utf-8 -*-

{
    'name' : 'Import Bill of  Materials (BOM) from Excel',
    'version': '7.1.5',
    'category': 'Manufacturing',
    'license': 'Other proprietary',
    'price': 39.0,
    'currency': 'EUR',
    'summary':  """This module allow you to import Multiple Bill of  Materials BOM from excel file.""",
    'description': """
Import Bill of  Material from Excel
This module allow you to Import Bill of Materials from excel file
import bom
bom import
bill of materials
import bill of material
import boms
import bom line
multiple bom import

    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/multiple_bom_import/904',#'https://youtu.be/0PzAAxJMY40',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/multipal_bom_import_wizard_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
