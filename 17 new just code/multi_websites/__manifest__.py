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
  "name"                 :  "Odoo Multi Website",
  "summary"              :  """Now operate multiple websites from single Odoo with Odoo multi website module. The module allows the customer to create multiple websites in Odoo and manage all of them separately.""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Multi-Website.html",
  "description"          :  """Odoo Multi Website Event Extension
Odoo Multi Website Blog Extension
Multi Website
Multi-Website
Multiple websites
Odoo multiple websites
Manage Multi website
Single Odoo multiple websites
Multi-Company
Multi-Warehouse
Multi-Theme
Multi-ecommerce
Multiple ecommerce
Multiple e-commerce""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=multi_websites",
  "depends"              :  ['website_sale', 'stock'],
  "data"                 :  [
                             'views/sale_order_view.xml',
                             'views/sale_stock_view.xml',
                             'views/res_partner_view.xml',
                             'views/website_view.xml',
                             'views/product_template.xml',
                             'views/payment.xml',
                            ],
  "demo"                 :  ['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}