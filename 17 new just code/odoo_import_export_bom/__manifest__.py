# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Import Export Bill of Materials Excel',
    'version': '7.1.4',
    'price': 39.0,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Manufacturing',
    'summary':  """This Module Allow to Import/Export Bill of Materials in Excel format.""",
    'description': """
Import Bills of Materials Line from Excel
This module import Bills of Materials line from excel file.
Export Bills of Materials In Excel  
This module export Bills of Materials.
import bom
bom import
Import Export Bill of Materials
export bom
import Bill of Materials
export Bill of Materials
Bill of Materials import
Bill of Material import
Bill of Material export
Bill of Materials export
bom import
    """,
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_import_export_bom/883',#'https://www.youtube.com/watch?v=HYjrVtrHPxA&feature=youtu.be',
    'external_dependencies': {'python': ['xlrd']},
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/bom_line_import.xml',
        'wizard/bom_export.xml',
        'views/bom_import_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 

