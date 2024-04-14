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
    "name":  "Royal Mail Proshipping Delivery Carrier",
    "summary":  """Royal Mail Pro Shipping enables you to conveniently ship and manage your 
                logistics delivery with the help of Royal Mail integration. Create a combined 
                order for deliveries using a cron scheduler for a day. Moreover, it allows logistics 
                operations for domestic and international shipping. The Odoo admin can add shipping 
                rates for delivery in Odoo.
                """,
    "category":  "Website/Shipping Logistics",
    "version":  "1.0.2",
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "https://store.webkul.com/odoo-royal-mail-proshipping-delivery-carrier.html",
    "description":  """Odoo Royal Mail Pro Shipping helps in conveniently delivering packages to customers 
                    located at different places. Quick and fast delivery with Royal Mail.
                    
                    Odoo, Odoo Apps, Odoo Admin, Odoo Shipping, Shipping Integration in Odoo, 
                    Shipping Integration, Delivery Carrier, Royal Mail, Royal Mail Pro Shipping, 
                    Odoo Royal Mail Pro Shipping, Royal Mail Post Integration in Odoo, Shipping, 
                    Package Delivery, Order Delivery, Order Shipping, Shipping Tracking, Royal Mail Tracking, 
                    Shipping Rates, Shipping Rate Calculator, Royal Mail Pro Delivery Carrier, 
                    Odoo Royal Mail Pro SHipping, Royal Mail Shipping, Royal Mail Pro
                    """,
    "live_test_url" :  "http://odoodemo.webkul.com/?module=royal_mail_proshipping_delivery_carrier",
    "depends":  [
        'odoo_shipping_service_apps',
    ],
    "data":  [
        'security/ir.model.access.csv',
        'views/proshipping_delivery_carrier.xml',
        'data/delivery.xml',
        'data/create_manifest_cron.xml',
    ],
    "images":  ['static/description/Banner.png'],
    "application":  True,
    "installable":  True,
    "price"      : 199,
    "currency":  "USD",
    "pre_init_hook":  "pre_init_check",
}
