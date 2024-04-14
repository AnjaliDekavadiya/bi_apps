# -*- coding: utf-8 -*-
{
    "name": """ POS discount authorization otp """,
    "summary": """Provides otp code for discount in POS""",
    "category": "Sales/OTP Discount",
    "version": "16.0.0.1.0.0",
    "author": "Digital Roots",
    "support": "sales@digitalroots.com.kw",
    "website": "https://digitalroots.com.kw",
    "license": "OPL-1",
    "depends": [
        "pos_discount",
        "point_of_sale",
        "dr_whatsapp_marketing"
    ],
    'price': 500.00,
    'currency': 'USD',
    "data": [
        'views/discount_otp_settings_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            "dr_discount_otp_auth/static/src/js/Screens/ProductScreen/CustomProductScreen.js",
            "dr_discount_otp_auth/static/src/js/Popups/SendOtpDialogPopup.js",
            "dr_discount_otp_auth/static/src/xml/Popups/SendOtpDialogPopup.xml"
        ]
    },
    'images': [
               'static/description/thumbnail.png',
               'static/description/discount_message.png',
               'static/description/discount_settings.png',
               'static/description/icon.png'],
    "auto_install": False,
    "installable": True,
}
