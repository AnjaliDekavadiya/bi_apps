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
  "name"                 :  "Odoo Marketplace Seller Store Pickup",
  "summary"              :  """Now, your Odoo Marketplace sellers can add multiple physical addresses so the customers can choose the preferred address and pickup their online store themselves.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Seller-Store-Pickup.html",
  "description"          :  """Locate store
Near me Seller address
Seller multiple address
Website store locator
Pick up order
Order pickup
Store order pickup
Website order
Multi seller locations
Seller physical location
Locate seller on map
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
Multi-seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_store_pickup&lifetime=120&lout=1&custom_url=/",
  "depends"              :  [
                             'marketplace_shipping_per_product',
                             'base_geolocalize',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/mp_store_setting.xml',
                             'views/inherit_seller_shop_view.xml',
                             'views/inherit_delivery_view.xml',
                             'views/inherit_mp_stock_view.xml',
                             'views/inherit_sale_view.xml',
                             'views/inherit_product_view.xml',
                             'views/template.xml',
                            ],
  "demo"                 :  [],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "assets"               :  {"web.assets_frontend":[
                              "marketplace_store_pickup/static/src/css/shop_style.css",
                              "marketplace_store_pickup/static/src/js/seller_store.js",
                              "marketplace_store_pickup/static/src/js/map_pickup.js",]
                              },
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "post_init_hook"       :  "assign_shop_group_to_seller",
}