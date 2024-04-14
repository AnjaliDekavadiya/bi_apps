# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': " Equipment Repair for Construction and Job Contracting in Odoo",
    'version': "17.0.0.0",
    'category': "Project",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'summary': "construction Equipment Repair machine repair for construction repair order repair job order construction repair construction product repair for job contracting job costing with repair project job costing repair management construction maintenance repair",
    'description': """
                        App for Construction
                        App for Contracting
                        maintance in construction 
                        App for Construction and Contracting
                        Repair App for Construction and Contracting
                     
                    """,
    'price': 29,
    'currency': 'EUR',
    'depends': ['base', 'project','bi_machine_repair_management', 'bi_odoo_job_costing_management',
                'bi_material_purchase_requisitions'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_repair_request_view.xml',
        'views/job_order_inherit_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'live_test_url': 'https://youtu.be/dQfxGwhSTmg',
    "images": ['static/description/Banner.gif'],
    'license':'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
