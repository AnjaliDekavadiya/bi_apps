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
    'name': 'Marketplace Facebook Catalog Integration',
    'version': '1.0.0',
    'sequence': 1,
    'description': 
    """
                    Marketplace Facebook Catalog Integration
                    Odoo Facebook Catalog Integration
                    Integrate Facebook Catalog with Odoo 
                    Facebook
                    Facebook Integration
                    Add Catalogs from Odoo to Facebook
                    Catalog in Facebook
    """,
    'summary': 'Marketplace Facebook Catalog Integration allows seller to send the products of odoo as feeds into facebook Market',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'store.webkul.com',
    'live_test_url': 'http://odoodemo.webkul.com/?module=marketplace_facebook_ads_feeds&lifetime=120&lout=0&custom_url=/web',
    'license': 'Other proprietary',
    'category': 'Website',
    'depends': [
        'odoo_marketplace',
        'facebook_ads_feeds'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/res_config.xml',
        'views/facebook_shop_view.xml',
        'views/fb_attachment.xml',
        'views/mp_seller_view.xml',
        'views/mp_product.xml'
    ],
    'images':['static/description/Banner.gif'],
    'auto_install': False,
    'application': True,
    'installable':True,
    'currency': 'USD',
    'price': 99,
    'pre_init_hook': 'pre_init_check',
    }
