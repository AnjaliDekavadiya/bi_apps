# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Material Purchase Requisitions Analysis/Trends Report',
    'currency': 'EUR',
    'version': '5.1.3',
    'license': 'Other proprietary',
    'price': 99.0,
    'summary': """This app allow user to do trending and anlysis on Material Purchase Requisitions from employees/departments.""",
    'description': """
Purchase Requisitions
Purchase Requisition
iProcurement
Inter-Organization Shipping Network
Online Requisitions
Requisition
Requisitions
product Requisitions
Requisitions trends
Requisition trend
trend Requisition
trend Requisitions
report Requisitions
report Requisition
employee Requisitions
employee Requisition
user Requisitions
user Requisition
Issue Enforcement
Inventory Replenishment Requisitions
Replenishment Requisitions
MRP Generated Requisitions
generated Requisitions
purchase Sales Orders
Complete Requisitions Status Visibility
Using purchase Requisitions
purchase requisitions
replenishment requisitions
employee Requisition
employee purchase Requisition
user Requisition
stock Requisition
inventory Requisition
warehouse Requisition
factory Requisition
department Requisition
manager Requisition
Submit requisition
Create purchase Orders
purchase Orders
product Requisition
item Requisition
material Requisition
product Requisitions
material purchase Requisition
material Requisition purchase
purchase material Requisition
product purchase Requisition
item Requisitions
material Requisitions
products Requisitions
purchase Requisition Process
Approving or Denying the purchase Requisition
Denying purchase Requisition​
construction managment
real estate management
construction app
Requisition
Requisitions
indent management
indent
indent stock
indent system
indent request
indent order
odoo indent
allow your employees to Create Purchase Requisition.
Employees can request multiple material/items on single purchase Requisition request.
Approval of Department Head.
Approval of Purchase Requisition Head.
Email notifications to Department Manager, Requisition Manager for approval.

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_purchase_requisitions_analysis/815',#'https://youtu.be/NwhHvRk8LAE',
    'category' : 'Project',
    'depends': [
        'material_purchase_requisitions',
    ],
    'data':[
        'security/ir.model.access.csv',
        'report/job_costing_trends.xml',
        'views/view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
