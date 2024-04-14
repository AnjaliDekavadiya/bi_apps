# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job Drawing Image Construction and Contracting Business in Odoo',
    'version': '17.0.0.0',
    'category': 'Project',
    'summary': 'Construction Image Drawing on construction Job Drawing Construction with Google Drawings job Drawing Contracting with Google Drawings on job costing Google Drawing on website my account page construction drawings construction image drawings job image draw',
    'description': """ Job Drawing Image Construction and Contracting Business
	
	Construction Drawing Image
Drawing Image
site Drawing Image
	
	 """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'price': 29,
    'currency': 'EUR',
    'images': [],
    'depends': ['base', 'bi_odoo_job_costing_management', 'bi_material_purchase_requisitions', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/show_image.xml',
        'views/job_order.xml',
        'views/web_template.xml'
    ],
    'qweb': [

    ],
    'web.assets_frontend': [
        'bi_job_drawing_image_contracting/static/src/**/*',
    ],
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/uQd_1jWBKNA',
    "images": ["static/description/Banner.gif"],
}
