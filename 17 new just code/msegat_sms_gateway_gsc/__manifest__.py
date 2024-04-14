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
    'name': 'Odoo Msegat SMS Gateway || SMS Marketing || SMS Gateway || Bulk SMS || SMS Integration',
    'version': '17.0.1.0.0',  # Version: odoo_version.odoo_sub_version.major_improvment.minor_improvment.bug_fixing
    'category': 'Tools',
    'license': 'OPL-1',

    # Summary Information
    # Summary: Approx 200 Char
    # Description: Can big
    'summary': """
Odoo Msegat SMS Gateway helps you integrate & manage Msegat SMS Accounts operations from Odoo. 
These apps Save your time, Resources, Effort, and Avoid manually manage multiple Msegat SMS Accounts to boost 
your business SMS Marketing with this connector.

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
Odoo Msegat SMS Gateway helps you integrate & manage Msegat SMS Accounts operations from Odoo. 
These apps Save your time, Resources, Effort, and Avoid manually manage multiple Msegat SMS Accounts to boost 
your business SMS Marketing with this connector.
        
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
    'support': 'growconsultancyservices@gmail.com',

    # Application Price Information
    'price': 50,
    'currency': 'EUR',

    # Dependencies
    'depends': ['base', 'sale_management', 'stock'],

    # Views
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/msegat_sms_account_view.xml',
        'views/msegat_sms_groups_view.xml',
        'data/ir_sequence.xml',
        'wizard/msegat_sms_template_preview_views.xml',
        'views/msegat_sms_template_view.xml',
        'views/msegat_sms_send_view.xml',
        'views/msegat_sms_log_history.xml',
        # 'views/'
        # 'wizard/'
    ],

    # Application Main Image    
    'images': ['static/description/app_profile_image.gif'],

    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
    'active': False,
}
