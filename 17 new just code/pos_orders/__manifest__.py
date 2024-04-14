# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name"              :  "POS All Orders List",
    "summary"           :  """POS All Orders List shows the list of orders placed in an Odoo POS session.
                              The user can also view customers' previous orders in the running POS session. Also, you can search for all orders by customer name or order reference number. The POS all order list module eases order searching and offers three different options to view orders; Load all past orders, load orders of current session, and load order of last 'n' days. Reorder list| POS Load previous orders| Past orders pos| Pos past orders| Orders POS session
                            """,
    "category"          :  "Point of Sale",
    "version"           :  "1.0.2",
    "sequence"          :  1,
    "author"            :  "Webkul Software Pvt. Ltd.",
    "license"           :  "Other proprietary",
    "website"           :  "https://store.webkul.com/Odoo-POS-All-Orders-List.html",
    "description"       :  """
                            POS all orders list allows you to view all the POS orders in the running POS session by searching by the customer name and order reference number.

                            """,
    "live_test_url"     :  "http://odoodemo.webkul.com/?module=pos_orders&custom_url=/pos/auto",
    "depends"           :  ['point_of_sale'],
    "data"              :  ['views/res_config_view.xml'],
    "demo"              :  ['data/pos_orders_demo.xml'],
    "images"            :  ['static/description/Banner.png'],
    "application"       :  True,
    "installable"       :  True,
    "assets"            :  {
                                'point_of_sale._assets_pos': [ 'pos_orders/static/src/**/*' ],
                            },
    "auto_install"      :  False,
    "price"             :  27,
    "currency"          :  "USD",
    "pre_init_hook"     :  "pre_init_check",
}