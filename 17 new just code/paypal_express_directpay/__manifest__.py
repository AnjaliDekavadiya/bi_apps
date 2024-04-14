# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name" : "Paypal Express Direct Pay",
    "summary" : "Integrate paypal express checkout payment gateway with ODOO for accepting payments from customers.",
    "category" : "Website",
    "version" : "1.0.0",
    "author" : "Webkul Software Pvt. Ltd.",
    "license" : "Other proprietary",
    "website" : "https://store.webkul.com/Odoo.html",
    "description" : """
        Paypal Express Direct Pay
        Paypal
        Paypal Express Direct Pay Payment Acquirer
        Odoo Paypal Express Direct Pay Payment Acquirer
        Paypal Express Direct Pay Payment Acquirer in Odoo
        Paypal Integration
        Odoo Paypal Express
        Paypal Express
        Paypal Express Direct Pay Integration
        Configure Paypal
        PayPal integration with Odoo
        Paypal Express Direct Pay Payment integration with Odoo
    """,
    "live_test_url" : "http://odoodemo.webkul.com/?module=paypal_express_directpay",
    "depends" : [
        'payment_paypal_express',
        'website_sale',
    ],
    "data" : [
        # 'security/ir.model.access.csv',
        'views/template.xml',
        'views/paypal_provider.xml',
        'data/paypal_config.xml',
    ],
    "images" : ['static/description/Banner.gif'],
    "application" : True,
    "installable" : True,
  "assets"               :  {"web.assets_frontend":["paypal_express_directpay/static/src/js/express_checkout.js",]},
    "price" : 46,
    "currency" : "USD",
    "pre_init_hook" : "pre_init_check",
}
