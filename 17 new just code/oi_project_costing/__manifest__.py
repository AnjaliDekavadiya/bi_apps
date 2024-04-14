# -*- coding: utf-8 -*-
{
'name': 'Project Costing',
'summary': 'Project Costing, Project Expense, Cost Sheet, Contracting, Planning, '
           'Planning Cost',
'version': '17.0.0.0.3',
'category': 'Project',
'website': 'https://www.open-inside.com',
'description': '''
        Project Costing
         
    ''',
'images': ['static/description/cover.png'],
'author': 'Openinside',
'license': 'OPL-1',
'price': 330.0,
'currency': 'USD',
'installable': True,
'depends': ['sale', 'project', 'hr_timesheet', 'sale_timesheet', 'stock'],
'data': ['security/ir.model.access.csv',
          'view/account_analytic_account.xml',
          'view/project_costing_category.xml',
          'view/sale_order.xml',
          'view/project_costing.xml',
          'view/product_category.xml',
          'view/hr_employee.xml',
          'view/actions.xml',
          'view/menu.xml',
          'data/project_costing_category.xml',
          'report/report.xml',
          'data/function.xml'],
'uninstall_hook': 'uninstall_hook',
'odoo-apps': True,
'application': False
}