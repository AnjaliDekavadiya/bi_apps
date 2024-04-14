# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Work Package for Construction and Contracting',
    'depends' : ['odoo_job_costing_management'],
    'version' : '7.39',
    'price': 10.0,
    'currency': 'EUR',
    # 'category': 'Project',
    'category': 'Services/Project',
    'license': 'Other proprietary',
    'summary': 'This app allow you to create and send work package to your customer.',
    'description': '''This Module Allow you to create job costing work package.
work order package
job order package
work package
job package
job costing
job cost sheet
cost sheet
construction
contracting
odoo contracting
job contracting
job costing
job sheet
job card
task package
job costing
job cost sheet
cost sheet
project cost sheet
project planning
project sheet cost
job costing plan
Construction cost sheet
Construction job cost sheet
Construction jobs
Construction job sheet
Construction material
Construction labour
Construction overheads
Construction sheet plan
costing
workshop
job workshop
workshop
jobs
cost centers
Construction purchase order
Construction activities
Basic Job Costing
Job Costing Example
job order costing
job order
job orders
Tracking Labor
Tracking Material
Tracking Overhead
overhead
material plan
job overhead
job labor
Job Cost Sheet
work package construction project
construction project
Engineering Work Package
EWP
Work Packs
package deal
Planning Package

    ''',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/wpjc.jpg'],
    # 'live_test_url': 'https://youtu.be/_5V33wJd9bo',
    # 'live_test_url':'https://youtu.be/XoRrFyW0xIE',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/job_costing_work_package/231',#'https://youtu.be/-LdF8hq_P0I',
    'data': [
            'security/ir.model.access.csv',
            'security/security_project_work.xml',
            'report/work_package_report_template.xml',
            'report/work_package_report.xml',
            # 'data/work_package_email_template.xml',
            # 'data/work_package_email_templates.xml',
            'data/work_package_email_templates_new.xml',
            'data/work_package_sequence_data.xml',
            # 'views/project_work_package.xml',
            'views/project_work_package_new.xml',
            'views/project_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
