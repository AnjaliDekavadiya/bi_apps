# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Project Task Images / Photo",
    'version': '5.2.1',
    'category': 'Operations/Project',
    'license': 'Other proprietary',
    'price': 9.0,
    'currency': 'EUR',
    'summary':  """Project Task Images and PDF Report in Odoo""",
    'description': """
This apps allow you to Print PDF Report for Project Task Image.
Project Task Images / Photo
task photos
task images
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/pt99.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_task_images_photos/988',#'https://youtu.be/EUZ9rw33u3g',
    'depends': ['project'],
    'data': [
          'views/project_view.xml',
          #'views/repair_template_report_view.xml',
            ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
