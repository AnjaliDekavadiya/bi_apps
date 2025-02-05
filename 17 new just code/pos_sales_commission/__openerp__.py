# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Sales Commission on Point of Sales',
    'version' : '1.0',
    'price' : 199.0,
    'currency': 'EUR',
    'category': 'Point Of Sale',
    'license': 'Other proprietary',
#     'live_test_url': 'https://youtu.be/-wK3ouvQw2I',
    'description': """
Sales Commission by Sales/Invoice/Payment

sales Commission
sale_commission
sales_Commission
sale Commission
sales Commissions
sales order Commission
order Commission
sales person Commission
sales team Commission
sale team Commission
sale person Commission
team Commission
Commission
sales order on Commission
invoice on Commission
payment on Commission
Commission invoice
Commission vendor invoice
sales Commision
Commission sales user invoice

Sales Commission (form)
Sales Commission (form)
Sales Commission List (tree)
Sales Commission List (tree)
Sales Commission Search (search)
Sales Commission Search (search)
sales_commission_id (qweb)
sales_commission_worksheet_id (qweb)

pos_sales Commission
pos_sale_commission
pos_sales_Commission
pos_sale Commission
POSsales Commissions
Pont of Sale sales Commission
POS order Commission
Point of Sale sales person Commission
POS sales team Commission
POS sale team Commission
POS sale person Commission
POS team Commission
POS Commission
POS sales order on Commission
POS invoice on Commission
POS payment on Commission
POS Commission invoice
POS Commission vendor invoice
POS sales Commission
POS Commission sales user invoice
POS Incentive
Sales Compensation 

POS Sales Commission (form)
POS Sales Commission List (tree)
POS Sales Commission Search (search)
POS sales_commission_id (qweb)
POS sales_commission_worksheet_id (qweb)


Sales Commission by Sales/Invoice/Payment

This module provide feature to manage sales commission by Sales/Invoice/Payments


This module allow company to manage sales commission with different options. You can configure after installing module what option/policy your company is following to give commissions to your sales users.
We are allowing you to select When to Pay and Calculation based on . Here you can define policy which will be used to give commission to your sales team.


For every Calculation based on we are allowing you to select:
1. Sales Manager Commission %
2. Sales Person Commission %

If you keep Sales Manager Commission 0% then system will not create sales commission lines and sales commission worksheet. System will work only with single option at time ie for example you can select When to Pay = Invoice confirm and calculation based on = POS Product category so system will run on that and create commission.

Please note that When to Pay = Customer payment is only supported with Calculation based on Sales Team. - Other options are supported in matrix. 
Workflow will be:
Option1 : Sales Confirmation -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every sales of current month, system will append sales commission lines on worksheet. -> End of month Account may review worksheet and create commission invoice to pay/release commission to sales person.
Option2 : Invoice Validate -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every invoice validation of current month, system will append sales commission lines on worksheet. -> End of month Account may review worksheet and create commission invoice to pay/release commission to sales person.
Option3 : Customer Payment -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every payment from customer of current month, system will append sales commission lines on worksheet. -> End of month Account may review worksheet and create commission invoice to pay/release commission to sales person.
Commission to sales person always will be in company currency. Multi currency is supported for this module so sales order/ invoice / payment can be in different currency but system will take care for it and create commission lines in company currency.
Sales Commission product is created using data and you still can change commission product on commission worksheet to create commission invoice.

Menus
---- Invoicing/Commissions
---- ---- Invoicing/Commissions/Commission Worksheets
---- ---- Invoicing/Commissions/Sales Commissions Lines
---- Point Of Sale/Commissions
---- ---- Point of Sale/Commissions/Commission Worksheets
---- ---- Point of Sale/Commissions/Sales Commissions Lines

Configuration for Sales Commission

Commission to sales person always will be in company currency. Multi currency is supported for this module so sales order/ invoice / payment can be in different currency but system will take care for it and create commission lines in company currency.
Sales Commission product is created using data and you still can change commission product on commission worksheet to create commission invoice.
Commission amount will be based on Net Revenue Model where it consider amounts without taxes. (This module does not support Gross Margin Model)

Point of Sale - Commission by Sales

This module provide feature to manage sales commission on Point Of Sales


This module allow company to manage POS sales commission with different options. You can configure after installing module what option/policy your company is following to give POS commissions to your POS sales users.
We are allowing you to select When to Pay and Calculation based on . Here you can define policy which will be used to give commission to POS sales team.

For every Calculation based on we are allowing you to select:
1. Sales Manager Commission %
2. Sales Person Commission %

If you keep Sales Manager Commission 0% then system will not create sales commission lines and sales commission worksheet. System will work only with single option at time ie for example you can select When to Pay = POS Order Paid and calculation based on = POS Product category so system will run on that and create commissions entries. 
Workflow will be: 
Option1 : POS Order Paid -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every POS sales of current month, system will append sales commission lines on worksheet. -> End of month Account may review worksheet and create commission invoice to pay/release commission to sales person and sales manager/leader.
Commission to sales person/leader always will be in company currency. Multi currency is supported by this module so POS order can be in different currency but system will take care for it and create commission lines in company currency.
Sales Commission product is created using data and you still can change commission product on commission worksheet to create commission invoice.
Commission amount will be based on Net Revenue Model where it consider amounts without taxes. (This module does not support Gross Margin Model)


Menus
---- Invoicing/Commissions
---- ---- Invoicing/Commissions/Commission Worksheets
---- ---- Invoicing/Commissions/Sales Commissions Lines
---- Point of Sale/Commissions
---- ---- Point of Sale/Commissions/Commission Worksheets
---- ---- Point of Sale/Commissions/Sales Commissions Lines

            """,
    'summary' : 'This module provide feature to manage sales commission on Point Of Sales.',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'wwww.probuse.com',
    'depends' : ['point_of_sale'],
    'support': 'contact@probuse.com',
    'data' : [
              'security/ir.model.access.csv',
              'security/pos_sales_commission_security.xml',
              'data/pos_commission_sequence.xml',
              'data/pos_product_data.xml',
              'view/pos_config_settings_views.xml',
              'view/crm_team_view.xml',
              'view/product_template_view.xml',
              'view/pos_category_view.xml',
              'view/pos_sales_commission_view.xml',
              'view/report_sales_commission.xml',
              'view/report_sales_commission_worksheet.xml',
              'view/pos_view.xml',
              'view/res_users_view.xml',
              'view/pos_config_view.xml'
              ],
    'installable' : True,
    'images': ['static/description/img.jpg'],
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
