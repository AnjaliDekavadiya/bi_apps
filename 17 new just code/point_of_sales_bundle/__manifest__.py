# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Point of Sale Related Apps',
    'price': 1.0,
    'version': '3.1.3',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This is package for Point of Sale Related Apps.""",
    'description': """
point of sales bundle
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'category' : 'Sales/Point Of Sale',
    'depends': [
        'import_pos_orders_excel',
        # 'odoo_pos_session_report_detail',
        'pos_customer_feedback_rating',
        'pos_lock_period',
        'pos_order_report',
        'pos_product_code',
        'pos_receipt_image_odoo',
        'pos_sale_item_info',
        'pos_sales_commission',
        # 'print_pos_session_report',
        'search_by_product_pos_order',
        'top_pos_by_items_customer',
        'website_portal_pos_orders',
        # 'point_of_sale_lock_password',
        ],
    'data':[
      
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
