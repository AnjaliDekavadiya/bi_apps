# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Document-Attachement Extension with Directory and Numbering',
	'summary': 'Document Extension with Directory Attachment Extension with Directory extension on document directory attachment directory document Numbering attachment Numbering Directory numbering on document version document management system DMS directory extension',
	'description': '''Attachment or Document Extension with Directory and Numbering in Odoo
	dms Job Contracting and Construction
	dms for Construction
	Document Extension with Directory and Numbering
	
	dms for Job Contracting and Construction
	Document Management System in Construction
	Document Management in Construction
	Document Management in Construction project
	manage documents in constructions
	manage documents in project constructions
	project documents management 
	project DMS
	
	 ''',
	'author': 'BrowseInfo',
    'price': 10,
    'currency': 'EUR',
	'website': 'https://www.browseinfo.com',
	'category': 'Document Management',
	'version': '17.0.0.1',
	'depends': ['base','mail','bi_odoo_document_version'],
	'data': [
			'security/ir.model.access.csv',
			'security/document_access.xml',
			'data/mail_tremplate.xml',
			'views/document_view.xml',
		],
	'installable': True,
	'application': True,
    'auto_install': False,
	'live_test_url' :'https://youtu.be/gShq8HvlSBw',
	'images':['static/description/Banner.gif'],
	'qweb': [
			],
	'license': 'OPL-1',

}
