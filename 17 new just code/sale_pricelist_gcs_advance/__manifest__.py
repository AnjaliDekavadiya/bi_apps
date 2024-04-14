# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#################################################################################
# Author      : Grow Consultancy Services (<https://www.growconsultancyservices.com/>)
# Copyright(c): 2021-Present Grow Consultancy Services
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
    # Application Information
    'name': 'Advance Product PriceList (Sales/Website/POS)',
    'version': '17.0.1.0.0',  # Version: odoo_version.odoo_sub_version.major_improvment.minor_improvment.bug_fixing
    'category': 'Sales',
    'license': 'OPL-1',

    # Summary Information
    # Summary: Approx 200 Char
    # Description: Can big
    'summary': """
This app allows you to extend the default pricelist by Only Category Level, Brand level along with Category, 
Only brand level, Category level along with Brand level. You can use this app with Sales orders, Website orders, 
POS orders, ...etc

GCS also provides various types of solutions, such as Odoo WooCommerce Integration, Odoo Shopify Integration,
Odoo Direct Print, Odoo Amazon Connector, Odoo eBay Odoo Integration, Odoo Amazon Integration,
Odoo Magento Integration, Dropshipper EDI Integration, Dropshipping EDI Integration, Shipping Integrations,
Odoo Shipstation Integration, Odoo GLS Integration, DPD Integration, FedEx Integration, Aramex Integration,
Soundcloud Integration, Website RMA, DHL Shipping, Bol.com Integration, Google Shopping/Merchant Integration,
Marketplace Integration, Payment Gateway Integration, Dashboard Ninja, Odoo Direct Print Pro, Odoo Printnode,
Dashboard Solution, Cloud Storage Solution, MailChimp Connector, PrestaShop Connector, Inventory Report,
Power BI, Odoo Saas, Quickbook Connector, Multi Vendor Management, BigCommerce Odoo Connector,
Rest API, Email Template, Website Theme, Various Website Solutions, SMS Gateway, SMS Marketing, SMS Integration, 
SMS OTP, Property/Real Estate Management, Hospital Managment, etc.
    """,
    'description': """ 
This app allows you to extend the default pricelist by Only Category Level, Brand level along with Category, 
Only brand level, Category level along with Brand level. You can use this app with Sales orders, Website orders, 
POS orders, ...etc

GCS also provides various types of solutions, such as Odoo WooCommerce Integration, Odoo Shopify Integration,
Odoo Direct Print, Odoo Amazon Connector, Odoo eBay Odoo Integration, Odoo Amazon Integration,
Odoo Magento Integration, Dropshipper EDI Integration, Dropshipping EDI Integration, Shipping Integrations,
Odoo Shipstation Integration, Odoo GLS Integration, DPD Integration, FedEx Integration, Aramex Integration,
Soundcloud Integration, Website RMA, DHL Shipping, Bol.com Integration, Google Shopping/Merchant Integration,
Marketplace Integration, Payment Gateway Integration, Dashboard Ninja, Odoo Direct Print Pro, Odoo Printnode,
Dashboard Solution, Cloud Storage Solution, MailChimp Connector, PrestaShop Connector, Inventory Report,
Power BI, Odoo Saas, Quickbook Connector, Multi Vendor Management, BigCommerce Odoo Connector,
Rest API, Email Template, Website Theme, Various Website Solutions, SMS Gateway, SMS Marketing, SMS Integration, 
SMS OTP, Property/Real Estate Management, Hospital Managment, etc.
    """,

    # Author Information
    'author': 'Grow Consultancy Services',
    'maintainer': 'Grow Consultancy Services',
    'website': 'http://www.growconsultancyservices.com',

    # Application Price Information
    'price': 45,
    'currency': 'EUR',

    # Dependencies
    'depends': ['point_of_sale', 'product_brand_gcs'],

    # Views
    'data': [
        'views/product_pricelist_views.xml'
        # 'view/'
        # wizard/
    ],
    'assets': {
        'point_of_sale.assets': [
            'sale_pricelist_gcs_advance/static/src/js/models.js',
        ],
    },

    # Application Main Image
    'images': ['static/description/app_profile_image.jpg'],

    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
    'active': False,
}
