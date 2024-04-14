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
  "name"                 :  "Odoo Marketplace PayPal Commerce",
  "summary"              :  "Odoo Marketplace PayPal Commerce For Odoo Marketplace - will split the payment among seller and admin dynamically.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "http://www.webkul.com",
  "description"          :  """
  Odoo Marketplace PayPal Commerce
  paypal payment getway
  payment getway
  payment getway for Odoo Marketplace
  Odoo Multi Vendor PayPal Commerce For Odoo Marketplace
  PayPal Commerce
  PayPal
  """,
  "live_test_url"        :  "http://odoodemo.webkul.com/demo_feedback?module=payment_paypal_commerce",
  "depends"              :  [
                             'website_payment',
                             'odoo_marketplace',
                            ],
  "data"                 :  [
                                'security/ir.model.access.csv',
                                'views/payment_views.xml',
                                'views/paypal_commerce_templates.xml',
                                'views/templates.xml',
                                'data/payment_provider_data.xml',
                                'data/seller_payment_method_data.xml',
                            ],
  "assets": {
        'web.assets_frontend': [
            'payment_paypal_commerce/static/src/js/frontent_commerce.js',
            'payment_paypal_commerce/static/src/css/frontent_commerce.css',
        ],
        'web.assets_backend': [
            'payment_paypal_commerce/static/src/xml/commerce.xml',
            'payment_paypal_commerce/static/src/js/backend_commerce.js',
            'payment_paypal_commerce/static/src/scss/backend_commerce.scss',
        ],
    },
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "post_init_hook"       :  "post_init_hook",
  "uninstall_hook"       :  "uninstall_hook",
  "external_dependencies":  {'python': ['PyJWT']},
}
