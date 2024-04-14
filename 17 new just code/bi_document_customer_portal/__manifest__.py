# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Document Management System - Customer/Partner Portal',
	'summary': 'Customer Portal Document Management Document my Account Partner portal document management Customer DMS Customer Document Partner Document Website Document management website document account website document portal system customer document portal system',
	'description': '''Document Management System - Customer Portal
	
	
	
	customer portal dms Job Contracting and Construction
	client dms for Construction
	
	Document Extension with Directory and Numbering
	
	dms for Job Contracting and Construction
	Document tags Management System in Construction
	Document Management in Construction
	Document Management in Construction project
	manage documents in constructions
	manage documents in project constructions
	project documents management 
	project DMS
	
	
	
	l''',	
	'author': 'BrowseInfo',
    'price': 39,
    'currency': 'EUR',
	'website': 'https://www.browseinfo.com',
	'category': 'Document Management',
	'version': '17.0.0.0',
	'depends': ['base',
				'bi_odoo_document_version',
				'bi_document',
				'bi_document_directory_extinsion_security',
				'website',
				],
	'data': [
			'security/ir.model.access.csv',
			'views/view_doc_portal.xml',
			'views/document_portal_view.xml',
		],
	'installable': True,
	'application': True,
    'auto_install': False,
	'live_test_url' :'https://youtu.be/4z2E1f5gyM8',
	'qweb': [
			],
	'images':['static/description/Banner.gif'],
	'license': 'OPL-1',
}
