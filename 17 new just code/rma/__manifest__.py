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
  "name"                 :  "Return Merchandise Authorization (RMA)",
  "summary"              :  """Odoo Website RMA. The module allows Odoo users to process product returns or product exchanges in Odoo.""",
  "category"             :  "Website",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Return-Merchandise-Authorization.html",
  "description"          :  """Odoo Website RMA
Odoo Website Return Merchandise Authorization
Return Merchandise Authorization in Odoo Website
RMA in Odoo
Website RMA
Returning products in Odoo website
Return Order
Return product
Exchange order
RMA number
Authorize Return Merchandise
Return Order Management
Order Replacement
Return Material Authorization
Order Return in Website""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=rma",
  "depends"              :  [
                             'sale_stock',
                             'website_sale',
                             'purchase',
                             'website_mail',
                            ],
  "data"                 :  [
                             'data/rma_creation_mail_to_admin.xml',
                             'data/rma_config_setting_data.xml',
                             'security/rma_security_view.xml',
                             'security/ir.model.access.csv',
                             'wizard/new_rma_wizard_view.xml',
                             'wizard/purchase_order_wizard_view.xml',
                             'wizard/product_return_view.xml',
                             'wizard/new_delivery_order_view.xml',
                             'wizard/new_mrp_repair_view.xml',
                             'views/res_config_view.xml',
                             'views/templates.xml',
                             'views/rma_view.xml',
                             'views/sequence.xml',
                             'views/sale_order_view.xml',
                             'views/res_partner_view.xml',
                             'report/report_rma.xml',
                             'report/rma_report.xml',
                             'demo/rma_demo.xml',
                            ],
  "demo"                 :  [
                             'demo/rma_user_demo_data.xml',
                             'demo/rma_rma_demo_data.xml',
                            ],
  'assets'               :  {
                                'web.assets_frontend': [
                                    'rma/static/src/css/rma.css',
                                    'rma/static/src/css/viewer.css',
                                    'https://cdnjs.cloudflare.com/ajax/libs/sweetalert/2.1.2/sweetalert.min.js',
                                    'rma/static/src/js/rma.js',
                                    'rma/static/src/js/viewer.js',
                                    '/rma/static/src/js/main.js',
                                 ],
                            },
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
