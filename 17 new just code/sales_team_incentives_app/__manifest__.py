# -*- coding: utf-8 -*-
{
	'name' : 'Salesman and Sales Team Incentives',
	'author': "Edge Technologies",
	'version' : '17.0.1.0',
	'live_test_url':'https://youtu.be/UEGcrTuUVLI',
	'images':['static/description/main_screenshot.png'],
	'summary' :'Sales team incentives for sales person incentives for salesman incentives on sale incentives total sales incentives for sales team apply incentives on sales target incentive for sale target sales commission sales team commission sale commission on sales',
	'description' : """Generate incentives for users based on how
	they perform and you can calculate incentives based on linear
	and tiered commission method.
	""",
	'depends' : ['base','crm','account','sale_management'],
	"license" : "OPL-1",
	'data' : [	
		'security/ir.model.access.csv',
		'views/crm_challenge.xml',
		'views/custom_accounting.xml',
		'views/crm_goal_details_views.xml',
		'views/crm_goals.xml',
		'views/crm_incentive_scheme.xml',
		'views/crm_incentive_calc.xml',
	],
	'qweb' : [],
	'demo' : [],
	'installable' : True,
	'auto_install' : False,
	'price': 45,
	'currency': "EUR",
	'category' : 'Sales',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
