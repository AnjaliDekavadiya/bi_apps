# Part of Softhealer Technologies.
{
    "name": "Call for Price To CRM lead | Lead Product To Quotation | Pipeline Product To Quotation",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "0.0.1",

    "category": "eCommerce",

    "license": "OPL-1",

    "summary": "Manage Product Price Hide Product Price Temporary Invisible Product Price Price Product Lead To Quotation Convert Pipeline Product To Quote Lead Products To Sale Order Automatic Add Lead Product In SO Lead Product To Quotation Odoo",
    "description": """Merchants occasionally have products and services where prices should be hidden for many reasons. These items might free, out of stock or their prices change frequently and need to be verified by phone, email and etc. The product prices will become a consensus between merchants and their customers. Call For Price is a tool with a flexible option, you can effectively manage all the product price status by deciding which are display, which must be contacted to know the price.The product that enables a call for the price will hide the price and "Add to cart" button, then add a button "Call for price". The customer clicks the button to send price requests to the merchant.  """,

    "depends": ['website_sale', 'website_sale_wishlist', 'website_sale_comparison', 'sh_crm_products_quote'],

    "data": [
        'security/call_for_price_crm_security.xml',
        'security/ir.model.access.csv',
        'views/website_sale_template_call_price.xml',
        'views/wishlist_tmpl.xml',
        'views/compare_tmpl.xml',
        'views/cart_tmpl.xml',
        'views/sale_call_for_price.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'sh_call_for_price_crm/static/src/js/sh_call_for_price_crm.js'
        ]
    },
    "images": ["static/description/background.png", ],

    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "35",
    "currency": "EUR"
}
