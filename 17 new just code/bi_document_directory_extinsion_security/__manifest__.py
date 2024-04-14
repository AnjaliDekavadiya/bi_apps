# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Document Management with Document numbering,Security and Tags in Odoo',
    'summary': 'Document numbering Document Tags Attachment numbering Attachment Tags DMS numbering DMS tagging Document extension document directory tag document number and tag document version attachment version attachment directory DMS directory of Document tag version',
    'description': '''Document Management with Document numbering and Tags
	
	dms Job Contracting and Construction
	dms for Construction
	Document Extension with Directory and Numbering
	
	dms for Job Contracting and Construction
	Document tags Management System in Construction
	Document Management in Construction
	Document Management in Construction project
	manage documents in constructions
	manage documents in project constructions
	project documents management 
	project DMS
	 ''',
    'author': 'BrowseInfo',
    'price': 19,
    'currency': 'EUR',
    'website': 'https://www.browseinfo.com',
    'category': 'Document Management',
    'version': '17.0.0.0',
    'depends': ['base',
                'bi_document',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/doc_directory_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/JP0GHI5bI_M',
    'images': ['static/description/Banner.gif'],
    'qweb': [
    ],
    'license': 'OPL-1',

}
