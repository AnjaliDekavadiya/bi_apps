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
    "name"              :  "Website Loyalty Program",
    "summary"           :  """The module helps to  win your customer loyalty .""",
    "category"          :  "Website",
    "version"           :  "1.0.0",
    "sequence"          :  1,
    "author"            :  "Webkul Software Pvt. Ltd.",
    "license"           :  "Other proprietary",
    "website"           :  "https://store.webkul.com/Odoo-Website-Loyalty-Management.html",
    "description"       :  """Odoo Website Loyalty Management For Website""",
    "live_test_url"     :  "http://odoodemo.webkul.com/?module=website_loyalty_management",
    "depends"           :  [
                            'website_virtual_product',
                            'wk_wizard_messages',
                            'portal',
                            'website_sale',
                            ],
    "data"              :  [
                            'security/ir.model.access.csv',
                            'views/res_config_view.xml',
                            'views/template.xml',
                            'views/website_loyalty_management.xml',
                            'data/data.xml',
                        ],
    "demo"              :  ['data/demo.xml'],
    'assets'            :  {
                            'web.assets_frontend': [
                                'website_loyalty_management/static/src/scss/style.scss',
                                'website_loyalty_management/static/src/js/website_loyalty_management.js',
                            ]},
    "images"            :  ['static/description/Banner.png'],
    "application"       :  True,
    "installable"       :  True,
    "price"             :  149,
    "currency"          :  "USD",
    "pre_init_hook"     :  "pre_init_check",
}
