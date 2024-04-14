# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Manufacturing Requisitions for Material',
    'version': '5.5',
    'price': 99.0,
    'category' : 'Manufacturing',
    'depends': [
        'material_purchase_requisitions',
        'mrp',
    ],

    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to create Requisition with create Manufacturing order option on Requisition lines""",
    'description': """

Manufacturing Material Requisition
production Material Requisition
mrp Material Requisition
Material Requisitions from Manufacturing / Workorder
Manufacturing Requisition
production Requisition
mrp Requisition
Manufacturing internal Requisition
production internal Requisition
mrp internal Requisition
work order Requisition
workorder Requisition
work order material Requisition

Manufacturing Requisitions
Manufacturing Requisition
production Requisitions
material Manufacturing Requisition
product Manufacturing Requisitions
mrp Requisition
product Requisition
Requisition mrp
Requisition Manufacturing
Manufacturing order Requisition
Material Requisitions from Manufacturing
employee Requisition
Purchase_Requisition_Via_iProcurement
Purchase Requisitions
Purchase Requisition
iProcurement
Inter-Organization Shipping Network
Online Requisitions
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
internal Requisitions
* INHERIT hr.department.form.view (form)
* INHERIT hr.employee.form.view (form)
* INHERIT stock.picking.form.view (form)
purchase.requisition search (search)
purchase.requisition.form.view (form)
purchase.requisition.view.tree (tree)
purchase_requisition (qweb)
Main Features:
allow your employees to Create Purchase Requisition.
Employees can request multiple material/items on single purchase Requisition request.
Approval of Department Head.
Approval of Purchase Requisition Head.
Email notifications to Department Manager, Requisition Manager for approval.
- Request for Purchase Requisition will go to stock/warehouse as internal picking / internal order and purchase order.
- Warehouse can dispatch material to employee location and if material not present then procurment will created by Odoo standard.
- Purchase Requisition user can decide whether product requested by employee will come from stock/warehouse directly or it needs to be purchase from vendor. So we have field on requisition lines where responsible can select Requisition action: 1. Purchase Order 2. Internal Picking. If option 1 is selected then system will create internal order / internal picking request and if option 2 is selected system will create multiple purchase order / RFQ to vendors selected on lines.
- For more details please see Video on live preview or ask us by email...


    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/material_manufacturing_requisitions/687',#'https://youtu.be/W_ErFPEk_80',
    'data':[
        'security/ir.model.access.csv',
        'wizard/mrp_production_requisition_view.xml',
        'views/material_requisition_view.xml',
        'views/mrp_production_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
