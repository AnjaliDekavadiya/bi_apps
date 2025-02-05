# -*- coding: utf-8 -*-
{

    'name': 'Tripple Approval Sales Quote and Order ',
    'version': '6.3.5',
    'category': 'Sales/Sales',
    'license': 'Other proprietary',
    'images': ['static/description/sota.jpg'],
    'price': 99.0,
    'currency': 'EUR',
    'depends': ['sale_management'],
    'data': [
            'security/ir.model.access.csv',
            'data/approve_mail_template.xml',
            'data/refuse_mail_template.xml',
            'security/sale_security.xml',
            'wizard/sale_order_refuse_wizard_view.xml',
            'views/sale_view.xml',
            # 'views/res_company_view.xml',
            'views/res_config_settings_view.xml',
             ],
    #'live_test_url': 'https://youtu.be/UHq8WUp0NZo',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/sale_tripple_approval/669',#'https://youtu.be/5n2CZ7kmuJs',
    'support': 'contact@probuse.com',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'summary': 'Approval Sales Order Tripple: Department Manager/Sales Manager -> Finance Manager -> Director Approval',
    'description' : '''
Added Finance Approval Start Range, Stop Range
Added Director Approval Start Range, Stop Range
sale approval flow
sale director approve
rfq
sale double approval
sale double approve
quote double approve
quote double approval
sale workflow
sale approve
sale order approve
quote approve
quotation approve
quotation approval
quote approval
salee manager approve
accounting approve
sales finanance approve
sales accounting approve
Director Approval
sales account deparement approve
sales approval
sales approve
sales workflow
sales workflow approval
User Validation For Sales
Sales Orde limit
sales flow
sales management
sales system
sales odoo
odoo sales
Sales order double validation
sales button
workflow sales
flow sales
approve sales
approval sales order
sales order approval flow
sales order director approve
sales order finanance approve
sales order accounting approve
sales order account deparement approve
sales order approval
sales order approve
sales order workflow
sales order workflow approval
sales order flow
sales order management
sales order system
sales order odoo
odoo sales order
sales order button
workflow sales order
flow sales order
approve sales order
Approval Sales Order Tripple: Sales Manager -> Finance Manager -> Director Approval.

System is flexible to have approval buttons based on amounts configured on company form. For example if sales amount less 5000 then in only required single level approval but if amount of sales order is greater then 5000 and less 8000 then it will need Sales manager + Finance manager approval..

Main Features
* Added Finance Approval Start Range, Stop Range.
* Added Director Approval Start Range, Stop Range.
Menus Available:

Sales
-- Sales/Orders Approval
-- Sales/Orders Approval/Department Approvals
-- Sales/Orders Approval/Director Approvals
-- Sales/Orders Approval/Finance Approvals
Invoicing
-- Invoicing/Sales/Orders Approval
-- Invoicing/Sales/Orders Approval/Finance Approvals

Sales Order Workflow Sample Example Users in Screens and Video

SO User ===> Denzel Washington
SO Sales/Department Manager ==> Johnny Depp
SO Finance Manager ==> Robert De Niro
SO Director Manager ==> Kevin Spacey
 
''',
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
