# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Construction Projects on Website in Odoo',
    'version': '17.0.0.0',
    'category': 'website',
    'license': 'OPL-1',
    "summary": "Construction Projects on Website Website Building Construction shop Website Construction Projects website Real Estate Management website building Construction Projects Construction Projects Show on Website project construction manage online Constructions",
    "description": """
    BrowseInfo developed a new odoo/OpenERP module apps.
    This module help to show Construction Projects on Website.
    This module use for Real Estate Management, Construction management, Building Construction,
    constuction projects
    Website Construction Projects
    Budgets
    Notes
    Materials
    Material Request For Job Orders
    Add Materials
    Job Orders
    Create Job Orders
    Job Order Related Notes
    Issues Related Project
    Vendors
    Vendors / Contractors
    Website Construction Management
    Website Construction Activity
    Website Construction Jobs

    Construction Management
    Construction agency
    manage Construction agency
    manage building Construction agency
    building Construction agency
    Construction agency management

    Construction Activity
    Construction Jobs
    Job Order Construction
    Job Orders Issues
    Job Order Notes
    Construction Notes
    Job Order Reports
    Construction Reports
    Job Order Note
    Construction app
    Project Report
    Task Report
    Construction Project - Project Manager
    real estate property
    propery management
    bill of material
    Material Planning On Job Order

    Bill of Quantity On Job Order
    Bill of Quantity construction
    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['base', 'sale', 'sale_management', 'project', 'portal', 'website', 'website_sale',
                'attachment_indexation'],
    'data': [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/project_view.xml",
        "views/website_project_template.xml",
    ],
    'demo': [],
    "price": 49,
    "currency": 'EUR',
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://youtu.be/NCESWLcYjBM',
    "images": ["static/description/Banner.gif"],
}
