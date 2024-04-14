# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Task Responsible by Stages on Project",
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_stage_responsible_user/926',#'https://youtu.be/nYrinv_axOU', 
    'price': 20.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Task  Responsible by Stages with Responsible User and Group on Project.""",
    'description': """
Assign Project to User and groups
Task Responsible by Stages
Task Responsible by Stages with Responsible User and Group
Assign Project to User and groups
Task Responsible by Stages
Task Responsible by Stages with Responsible User and Group
Task Responsible by Stages on Project
Task Responsible by Stages with Responsible User and Group on Project.
This module will allow project manager to configure project and add possiblities to setting Responsible users on every stage and also project manager can set groups so that it won't allow someone who does not have access to that group and try to move to that stage. Please note that if any stage which are not configured on Responsibility By Stages then our app won't do anything for that stage and will follow Odoo default behaviour.
Project Form Configuration - Responsibility By Stages
project security
task security
security
project by user
task by user
by user
task by stages
by stage
project by stages
project by stages
task stages
stages
project stages
Responsible User
Group on Project

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'category': 'Project',
    'version': '5.1.23',
    #'depends': ['project_issue'],
    'depends': ['project'],
    'data':[
        'security/ir.model.access.csv',
        'views/project_stage_security.xml',
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
