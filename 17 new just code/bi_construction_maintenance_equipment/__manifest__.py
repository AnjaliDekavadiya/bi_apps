# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': "Construction Contracting MRO with Equipment and Maintenance in Odoo",
    'version': '17.0.0.0',
    'category': 'Project',
    'summary': 'Apps for construction MRO Maintenance Equipment Maintenance Management Equipment MRO system Equipment repair Management in construction mro construction Equipment repair machine repair construction repair checklist repair material mro repair Maintenance',
    'description': """Construction and Contracting with Equipment & Maintenance
	
	Construction Equipment Maintenance Management
	Construction Mro 
	project MRO 
	project Equipment Maintenance Management
	project Equipment Management
	Mro in Odoo
	
	Equipment Management in Odoo
	
	Equipments Management
	
	
	""",
    'author': "BrowseInfo",
    'website': 'https://www.browseinfo.com',
    'price': 19,
    'currency': 'EUR',
    'depends': ['base', 'bi_material_purchase_requisitions', 'bi_website_job_workorder', 'maintenance',
                'bi_mro_maintenance_management'],
    'data': [
        'views/job_orders_view.xml',
    ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/rv4wWjyCJaE',
    "images": ["static/description/Banner.gif"],
    'license': 'OPL-1',
}
