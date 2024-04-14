# -*- coding: utf-8 -*-
{
    "name": "Point Of Sale Smart Cash",
    "author": "Datanalisis Consultores, SL",
    "website": "https://www.smarthoreca.es/",
    "support": "soporte@datanalisis.es",
    "license": "OPL-1",
    "category": "Point of Sale",
    "summary": " ",
    "description": """  """,
    "version": "17.0.0.0.1",
    "depends": ["point_of_sale", "pos_payment_config"],
    "application": True,
    "data": [
        'views/pos_config.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_smart_cash/static/**/*',                                ], 
    },
    "images": ["static/description/smart_cash_screenshot.jpg", ],
    "auto_install": False,
    "installable": True,
    "price": 900,
    "currency": "EUR"
}
