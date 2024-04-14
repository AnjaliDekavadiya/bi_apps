# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Point Of Sale Partial Payment",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "point of sale",
    "license": "OPL-1",
    "summary": "Partial Payment Point Of Sale Partial Payment POS Partial Payment Invoice Partial Payment Invoice Reconciliation Payment Half Payment POS Partially Payment Odoo Partial Invoice Payment",
    "description": """Using this module customers can pay a partial payment of order. You can restricts the partially payment for all customers and you can allow partial payment feature for special customers as well. We provide filter option to filter partial payment from all the payments.""",
    "version": "0.0.1",
    "depends": ["sh_pos_order_list"],
    "application": True,
    "data": [
        'data/product_product_data.xml',
        'views/account_move_views.xml',
        'views/pos_order_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'sh_pos_partial_payment/static/src/overrides/**/*',
        ]
    },
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "price": 80,
    "installable": True,
}
