# -*- coding: utf-8 -*-
# Copyright 2023 IZI PT Solusi Usaha Mudah
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# noinspection PyUnresolvedReferences,SpellCheckingInspection
{
    "name": """Tiktok Shop Connector""",
    "summary": """Integrating Odoo with Marketplace: Tiktok""",
    "category": "Sales",
    "version": "17.0.1.1.1",
    "development_status": "Beta",  # Options: Alpha|Beta|Production/Stable|Mature
    "auto_install": False,
    "installable": True,
    "application": True,
    "sequence": -99,
    "author": "IZI PT Solusi Usaha Mudah",
    "support": "admin@iziapp.id",
    "website": "https://www.iziapp.id",
    "module_type": "official",
    "license": "OPL-1",
    "images": [
        'static/description/banner.gif'
    ],
    "price": 1100,
    "currency": "USD",

    # any module necessary for this one to work correctly
    'depends': ['base', 'izi_marketplace'],

    # always loaded
    'data': [
        # data
        'data/data_tiktok_state_order.xml',
        'data/mp_partner.xml',

        'wizard/wiz_tiktok_order_reject.xml',
        'views/action/action_menu.xml',
        'views/mp_account.xml',
        'views/menu.xml',
        'views/mp_tiktok_shop.xml',
        'views/mp_tiktok_logistic.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/mp_product.xml',

        # 'views/wizard/views.xml',

        'security/ir.model.access.csv',
        'security2/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    
    "post_load": None,
    # "pre_init_hook": "pre_init_hook",
    # "post_init_hook": "post_init_hook",
    "uninstall_hook": None,

    "external_dependencies": {"python": [], "bin": []},
}
