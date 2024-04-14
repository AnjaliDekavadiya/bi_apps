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
  "name"                 :  "Website Payment PayPal Recurring",
  "summary"              :  "Website Payment PayPal Recurring",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "description" : """
        Website Payment PayPal Recurring
        Paypal Subscription
        Subscription using Paypal
        Subscription
        Paypal
        PayPal Recurring
        Website Payment PayPal Recurring Acquirer
        Odoo Payment PayPal Recurring Pay Payment Acquirer
        Payment PayPal Recurring Payment Acquirer in Odoo
        Paypal Integration
        Odoo Paypal Recurring
        Paypal Recurring
        Website Payment PayPal Recurring Integration
        Configure Paypal
        PayPal integration with Odoo
        Website Payment PayPal Recurring Payment integration with Odoo
    """,
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_paypal_recurring&custom_url=/shop",
  "depends"              :  [
                                'payment_paypal_express',
                                'website_subscription_management',
                            ],
  "data"                 :  [
                                'views/template.xml',
                                'views/provider_view.xml',
                                'views/provider_template.xml',
                                'data/paypal_recurring_demo_data.xml',
                            ],
  "assets"               : {
                              'web.assets_frontend': [
                                      'payment_paypal_recurring/static/src/js/paypal_recurring.js',
                                    ],
                            },
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "USD",
  "pre_init_hook":  "pre_init_check",
}
