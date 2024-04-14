# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
	'name'    : 'Odoo Hubspot Bridge',
	'category': 'CRM',
	'version' : '1.3.3',
	'sequence': 10,
	'author'  : 'Webkul Software Pvt. Ltd.',
	'license' : 'Other proprietary',

	'summary'    : '',
	'description': """
	Odoo Hubspot Connector
	Odoo Hubspot Bridge
	Odoo Hubspot Solution
	Odoo Hubspot Integration
    Hubspot
	hubspot dashboard
	""",

	'website': 'https://store.webkul.com/odoo-multi-crm-hubspot-solution.html',
	'live_test_url': 'https://odoodemo.webkul.com/demo_feedback?module=hubspot_odoo_bridge',

	'depends': ['odoo_multi_channel_crm'],
	'data'   : [
        'security/ir.model.access.csv',
		'wizard/channel_import.xml',
		'views/connection.xml',
		'data/connection.xml',
        'views/activity_mapping.xml',
        'views/mapping/lead_activity_mapping.xml',
        'views/mapping/partner_activity_mapping.xml'
	],

	'images'               : ['static/description/Banner.png'],
	'application'          : True,
	'price'                : 100,
	'currency'             : 'USD',
	'external_dependencies': {'python': ['hubspot-api-client']},
	'pre_init_hook'        : 'pre_init_check',
}
