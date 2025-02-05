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
  "name"                 :  "Website Coupons & Vouchers",
  "summary"              :  """The module allows you to create discount coupons and vouchers for Odoo website. The voucher code can be used by the customer to obtain discount on orders.""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Voucher.html",
  "description"          :  """Odoo Website Coupons & Vouchers
Website coupons
Website vouchers
Voucher code
Coupon code
Manage vouchers
Discount coupons
Discount vouchers
Sale vouchers
Coupons & vouchers
POS discount sale
coupon discount
Give discount on Website
Website discount coupons
Odoo Website discount
Discount code Website""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_voucher",
  "depends"              :  [
                             'wk_coupons',
                             'website_sale',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'wizard/voucher_wizard_view.xml',
                             'views/templates.xml',
                             'views/coupon_inherited_view.xml',
                             'views/inherited_sale_order_view.xml',
                             'views/res_config_view.xml'
                            ],
  "assets"               : {'web.assets_frontend':["/website_voucher/static/src/js/voucher.js",
                                                        "/website_voucher/static/src/css/voucher.css"
                                                        ]

                            },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  124,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
