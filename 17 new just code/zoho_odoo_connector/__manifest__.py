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
    "name":  "ZohoBook Odoo Connector",
    "summary":  """
                    Odoo Multi Accounting Zoho Connector allows users to import/export 
                    data of accounting that has already been created using cron or by 
                    manual transfer
                    odoo connector zoho accounting webkul multiaccounting zoho multi accounting 
                    odoo accounting solutions zoho book zohobook odoo webkul apps
                """,
    "category":  "Website",
    "version":  "1.1.0",
    'depends': [
        'odoo_multi_accounting_solution'
    ],
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "data":  [
        "data/demo.xml",
        "views/core/zoc_account_move_view.xml",
        "views/core/zoc_purchase_order_view.xml",
        "views/core/zoc_sale_order_view.xml",
        "views/core/zoc_omas_view.xml",
    ],
    'images': ['static/description/banner.gif'],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
    "price":  150,
    "currency":  "USD",
    "pre_init_hook":  "pre_init_check",
    "live_test_url":  "http://odoodemo.webkul.com/?module=zoho_odoo_connector",
}
