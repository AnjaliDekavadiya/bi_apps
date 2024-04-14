# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Document Portal for Job Costing and Contracting',
    'summary': 'Document Management for Job Contracting Document Construction Document portal for job costing DMS job contracting document management system construction document version construction document tag job costing document directory for construction contract',
    'description': '''Document Management for Job Contracting and Construction 
	dms Job Contracting and Construction
	dms for Construction
	dms for Job Contracting and Construction
	Document Management System in Construction
	Document Management in Construction
	Document Management in Construction project
	manage documents in constructions
	manage documents in project constructions
	project documents management 
	project DMS
	
	
	
For Job Contracting and Construction
	
	''',
    'author': 'BrowseInfo',
    'price': 19,
    'currency': 'EUR',
    'website': 'https://www.browseinfo.com',
    'category': 'Projects',
    'version': '17.0.0.0',
    'depends': ['base',
                'bi_material_purchase_requisitions',
                'bi_odoo_job_costing_management',
                'bi_odoo_document_version',
                'bi_document_customer_portal',
                'mail'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/job_document_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/p9-sHNaEZ-U',
    'images': ['static/description/Banner.gif'],
    'license': 'OPL-1',
}
