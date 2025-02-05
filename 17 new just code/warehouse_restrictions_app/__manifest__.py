# -*- coding: utf-8 -*-
{
    'name': 'Warehouse Restrictions App',
    'author': 'Edge Technologies',
    'version': '17.0.1.1',
    'live_test_url':'https://youtu.be/WM2Y9NZy3U8',
    "images":['static/description/main_screenshot.png'],
    'summary': 'Warehouse user restrictions user warehouse restriction for user warehouse location restrict location on warehouse location restrictions warehouse stock restriction warehouse stock location restriction inventory restriction inventory location restriction',
    'description': """Warehouse restrictions app""",
    "license" : "OPL-1",
    'depends': ['base','sale_management','stock','account'],
    'data': [
        'security/warehouse_restrictions_group.xml',
        'security/warehouse_restrictions_rules.xml',
        'views/warehouse_restrict_views.xml',
    ],
    'qweb' : [],
    'demo': [],
    'css': [],
    'installable': True,
    'auto_install': False,
    'price':20,
    'currency': "EUR",
    'category': 'Warehouse',
}
