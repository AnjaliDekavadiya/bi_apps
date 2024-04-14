# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "MRO Equipment Maintenance Management in Odoo",
    'version': '17.0.0.0',
    'category': 'Project',
    'summary': 'Apps for construction MRO Maintenance Equipment Maintenance Management Equipment MRO system Equipment repair Management in construction mro construction Equipment repair machine repair construction repair checklist repair material mro repair Maintenance',
    'description': """MRO - Equipment Maintenance Management
	
	""",
    'author': "BrowseInfo",
    'website': 'https://www.browseinfo.com',
    'price': 19,
    'currency': 'EUR',
    'depends': ['base', 'bi_material_purchase_requisitions', 'bi_website_job_workorder', 'maintenance', ],
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_checklists_list_config_view.xml',
        'views/equipment_view.xml',
        'views/maintenance_request_view.xml',
        'views/job_orders_view.xml',
    ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/97nhyGxlo8A',
    "images": ["static/description/Banner.gif"],
	'license':'OPL-1',
}
