{
    'name': 'POS Restaurant User Access',
    'version': '17.0.2.0',
    'summary': """User Access to Closing POS Restaurant, Order Deletion, Order Line Deletion,
                  Discount Application, Order Payment, Price Change and Decreasing Quantity,
Odoo POS validation, Odoo POS validate, Odoo POS confirmation, Odoo POS confirm,
Odoo POS checking, Odoo POS check, Odoo POS access, Odoo POS user, user access, access right,
delete order, delete order line, POS closing, closing POS, decrease quantity, POS Cash In/Out,
POS Cash Out/In""",
    'description': """
POS Restaurant User Access
==========================

This module allows restrictions on some features in POS UI if the cashier has no access rights

Per user, you can define access/restriction for the following features:
* POS Closing - When any order has been sent to kitchen but unpaid
* Order Deletion - When the current order has been sent to kitchen but unpaid
* Order Line Deletion - When the current order line has been sent to kitchen
* Decreasing Quantity - When the current order line has been sent to kitchen
""",
    'category': 'Sales/Point of Sale',
    'author': 'MAC5',
    'contributors': ['MAC5'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'pos_restaurant',
        'pos_user_access_mac5',
    ],
    'data': [
        'views/res_users_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_restaurant_user_access_mac5/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 20.00,
    'currency': 'EUR',
    'support': 'mac5_odoo@outlook.com',
    'license': 'OPL-1',
    'live_test_url': 'https://youtu.be/Qfdx0N7-0XM',
}
