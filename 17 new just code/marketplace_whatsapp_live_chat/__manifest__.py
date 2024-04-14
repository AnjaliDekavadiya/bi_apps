# -*- coding: utf-8 -*-
##########################################################################
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
##########################################################################
{
    'name'          : 'Marketplace Whatsapp Live Chat',
    'version'       : '1.0.0',
    'description'   : """
        Marketplace Whatsapp Live Chat
        whatsapp
        whatsapp integration
        whatsapp support
        marketplace whatsapp support
    """,
    'summary'       : 'Sellers can provide whatsapp support to the customers.',
    'author'        : 'Webkul Software Pvt. Ltd.',
    'sequence'      : 1,
    'website'       : 'store.webkul.com/Odoo.html',
    'license'       : 'Other proprietary',
    'category'      : 'website',
    'live_test_url' : 'http://odoodemo.webkul.com/?module=marketplace_whatsapp_live_chat&lifetime=120&lout=1&custom_url=/',
    'depends'       : [
        'odoo_whatsapp_live_chat',
        'odoo_marketplace'
    ],
    'data'          : [
        'views/mp_seller_view.xml',
        'views/templates.xml'
    ],
    "assets"              :{
        'web.assets_backend':['marketplace_whatsapp_live_chat/static/src/js/mp_whatsapp.js',
                                ]
    },
    'images'        : ['static/description/Banner.gif'],
    'auto_install'  : False,
    'installable'   : True,
    'application'   : True,
    'currency'      : 'USD',
    'price'         : 45,
    'pre_init_hook' : 'pre_init_check'
}
