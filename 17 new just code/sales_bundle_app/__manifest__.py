# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Bundle of Sales Related Apps",
    'version': '3.2.4',
    'price': 1.0,
    'currency': 'EUR',
    'category' : 'Sales/Sales',
    'license': 'Other proprietary',
    'summary': """This module contains bundle of Sales Related Apps/Modules.""",
    'description': """
Sales apps
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/sb1.jpg'],
    'depends': [
        # 'blanket_sales_order',
        'bulk_sale_order_confirm',
        'mass_cancel_sale_purchase_order',
        'multiple_sales_person_group',
        'odoo_sale_cancel_reason',
        'odoo_sale_order_merge',
        'odoo_sales_quotation_number',
        'open_order_by_sales_person',
        'product_sale_stock_warning',
        'replacement_order_sales',
        'sale_order_import_excel',
        'sale_purchase_inventory_tags',
        'sale_purchase_last_price',
        'sale_purchase_order_history',
        'sale_purchase_order_image',
        'sale_purchase_product_history',
        'sale_team_order_access',
        'sale_tripple_approval',
        'sales_order_stages_odoo',
        'sales_person_customer_access',
        'top_sales_by_item_customer',
        'sales_team_customer_access',
    ],
    'data':[
        
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
