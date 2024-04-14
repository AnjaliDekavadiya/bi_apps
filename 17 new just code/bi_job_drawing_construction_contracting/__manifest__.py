# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Job Drawing Construction and Contracting Business in Odoo',
    'version': '17.0.0.0',
    'category': 'Project',
    'summary': 'Job Drawing Construction with Google Drawings job Drawing Contracting Business with Google Drawings on job costing Google Drawing on website my account page Construction Google Drawings for job costing construction drawings construction site drawings',
    'description': """ Job Drawing Construction and Contracting Business construction drawings site drawings """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'price': 19,
    'currency': 'EUR',
    'images': [],
    'depends': ['base', 'bi_odoo_job_costing_management', 'bi_material_purchase_requisitions', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/job_order.xml',
        'views/web_template.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/xTKhEYn2TzU',
    "images": ["static/description/Banner.gif"],
    'license': 'OPL-1',
}
