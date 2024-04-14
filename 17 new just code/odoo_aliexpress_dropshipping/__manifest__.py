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
  "name"                 :  "Odoo Aliexpress Dropshipping",
  "summary"              :  """With this module, you can now accept dropship orders for aliexpress on Odoo website. The customers can place orders for aliexpress products and you can forward them the Aliexpress website.""",
  "category"             :  "Website",
  "version"              :  "1.2.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-aliexpress-dropshipping.html",
  "description"          :  """Dropshipper
Drop ship orders
Dropshipping
Odoo drop ship
Dropship delivery
Aliexpress integration
Odoo aliexpress dropship
Aliexpress delivery
Orders for aliexpress
Odoo dropshipping integration
Accept dropship orders
Import aliexpress products""",
  "live_test_url"        :  "https://odoodemo.webkul.com/?module=odoo_aliexpress_dropshipping",
  "depends"              :  [
                             'website_sale_stock',
                             'variant_price_extra',
                            ],
  "data"                 :  [
                             'security/aliexpress_security.xml',
                             'security/ir.model.access.csv',
                             'data/config_data.xml',
                             'views/res_users_view.xml',
                             'views/product_view.xml',
                             'views/aliexpress_products_view.xml',
                             'views/res_config_view.xml',
                             'views/sale_view.xml',
                             'views/menus_view.xml',
                             'views/template.xml',
                             'views/aliexpress_cron_view.xml',
                            ],
  "assets"            : {
        'web.assets_frontend':[
            'odoo_aliexpress_dropshipping/static/src/css/ali_product.css'
        ]
    },
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
