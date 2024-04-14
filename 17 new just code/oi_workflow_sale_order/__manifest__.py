# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Workflow Approval',
    'summary': 'Sales Order Workflow, Highly Configurable and Flexible approval '
    'cycle/process for Sales Orders, Sales Approval, SO Approval Process, '
    'Approval Cycle, Approval Process, Sales Order, Approval Workflow, Approve '
    'Sales Order, Approve SO, Sales Manager, Multi-level Approval Process, Sales '
    'Approval Flow, Approval Rules, Manager Approval',
    'version': '17.0.0.0.0',
    'category': 'Sales',
    'website': 'https://www.open-inside.com',
    'description': '''
		Sale Order Workflow Approval
		 
    ''',
    'images': ['static/description/cover.png'],
    'author': 'Openinside',
    'license': 'OPL-1',
    'price': 9.99,
    'currency': 'USD',
    'installable': True,
    'depends': ['sale', 'oi_workflow'],
    'data': ['view/sale_order.xml', 'data/approval_config.xml'],
    'uninstall_hook': 'uninstall_hook',
    'odoo-apps': True,
    'application': False
}
