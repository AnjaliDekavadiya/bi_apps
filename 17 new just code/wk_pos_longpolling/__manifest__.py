# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

{
  "name"                 :  "POS Realtime Update",
  "summary"              :  "POS Realtime Update, used to send real time notifications in the pos. It will update the pos product, customer, pricelist items and account taxes data in real time. It will require to enable the websocket. Pos Product Update |Pos Customer Update| Pos Pricelist Items| Pos Account Taxes |Pos Partner Data",
  "category"             :  "Point Of Sale",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "description"          :  """
                            POS Realtime Update
                            POS Websocket
                            POS Realtime
                            Pos Product Update |
                            Pos Customer Update|
                            Pos Pricelist Items|
                            Pos Account Taxes |
                            Pos Partner Data
                            Product  
                            Pricelist 
                            taxes 
                            Customers
                            """,
  "depends"              :  [
                             'bus',
                             'point_of_sale'
                            ],
  "data"                 :  [
                              'security/ir.model.access.csv',
                              'data/cron.xml',
                              'views/pos_common_changes_view.xml',
                              'views/pos_config_view.xml',
                              
                            ],
  'assets': {
        'point_of_sale._assets_pos': [
            "wk_pos_longpolling/static/src/**/*",
        ],
  },
  "images"               :  ['static/description/Banner.png'],
  "website"              :  "https://store.webkul.com/",
  "live_test_url"        :  "https://odoodemo.webkul.com/demo_feedback?module=wk_pos_longpolling",
  "license"              :  "Other proprietary",
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "currency"             :  "USD",
  "price"                :  99,
  "pre_init_hook"        :  "pre_init_check"
}
