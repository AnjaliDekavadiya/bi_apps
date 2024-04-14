# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Meeting Minutes For Construction Projects',	
	'summary': 'Apps Meeting Minutes Print Meeting Minutes print meetings minutes print minutes meetings for construction project print minutes of meetings contracting print construction Meeting Minutes pdf report Contracting Meeting Minutes Print project meeting report',
	'description': '''Meeting Minutes for Construction and Contracating Projects ''',
	'author': 'BrowseInfo',
	'website': 'https://www.browseinfo.com',
	'category': 'Project',
	"price": 10,
	"currency": 'EUR',
	'version': '17.0.0.0',
	'depends': ['base',
				'calendar',
				'bi_meeting_minutes',
				'bi_material_purchase_requisitions',
				'bi_odoo_job_costing_management',
				'bi_subtask',
			],
	'data': [
		'security/ir.model.access.csv',
		'views/view_meeting_project.xml',
		'report/report_meeting_proj.xml',
		'report/report_meeting_proj_template.xml',
		],

	'license': 'OPL-1',
	'installable': True,
	'application': True,
	'auto_install': False,
	'live_test_url' :'https://youtu.be/XQZG6N4EqQ0',
	'qweb': [
			],
	"images":["static/description/Banner.gif"],
}

