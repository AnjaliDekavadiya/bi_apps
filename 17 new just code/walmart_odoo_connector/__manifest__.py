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
  "name"                 :  "Walmart Odoo Connector | Odoo Multichannel",
  "summary"              :  """Integrate Walmart marketplace with Odoo. Configure you Walmart store with Odoo. Manage orders, products, etc at Odoo’s end.
multi channel multi-channel walmart multichannel walmart bridge walmart connector walmart odoo bridge odoo walmart extensions for multichannel""",
  "category"             :  "Website",
  "version"              :  "2.1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Multichannel-Walmart-Connector.html",
  "description"          :  """https://webkul.com/blog/?s=odoo+multichannel&cat=Odoo
    Walmart integration
		Walmart Connector
		Walmart Odoo Bridge
		Connect Walmart
		Walmart bridge
		Walmart to Odoo
		Manage orders
		Manage products
		Import products
		Import customers
		Import orders""",
  "live_test_url"        :  "https://odoodemo.webkul.com/?module=walmart_odoo_connector",
  "depends"              :  ["odoo_multi_channel_sale"],
  "data"                 :  [
                            "security/ir.model.access.csv",
                             "data/cron.xml",
                             "views/multi_channel_sale.xml",
                             "views/product.xml",
                             "views/mapping.xml",
                             "wizard/import_operation.xml",
                             "wizard/export_template.xml",
                             "wizard/export_product.xml",
                             "data/demo.xml",
                            #  "data/attribute_mappings.xml",
                            #  "data/category_mapping.xml",
                             "wizard/walmart_feed.xml",
                            ],
  "assets": {
    "web.assets_qweb": [
      "walmart_odoo_connector/static/src/xml/*.xml",
    ],
  },
  'assets': {
      'web.assets_backend': [
        "walmart_odoo_connector/static/src/xml/instance_dashboard.xml",
    ],
    },
  "images"               :  ["static/description/banner.gif"],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  370.0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
