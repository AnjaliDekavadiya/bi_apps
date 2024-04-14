# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Fabric Collect and Delivery for Cloth Tailor',
    'version' : '5.1.2',
    'price' : 79.0,
    'currency': 'EUR',
    'category': 'Inventory/Inventory',
    'license': 'Other proprietary',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/cloth_tailor_picking_manage/442',#'https://youtu.be/OZFsVGrMoLI',
    'images': [
        'static/description/img.jpg',
    ],
    'summary' : 'Receive cloth fabric and deliver cloth to your customer using incoming and outgoing shipment.',
    'description': """
This app allows you to manage your customers receive cloth fabric and deliver cloth to  your customer using incoming and outgoing shipment of Odoo inventory.
    - This app adds a “Receive Fabric” & “Deliver Cloth” button on cloth request form as shown in below screenshots.
    - This app creates incoming picking shipments to receive fabric material from your customer. Basically when a customer comes with fabric to make cloth tailoring then you can create and receive fabric using incoming shipment of inventory.
    - This app creates outgoing picking shipments to deliver material to your customer. Basically when a customer comes in to get clothes after tailoring is done then you can create and deliver cloth using outgoing shipment of inventory.
    - This app shows ‘Incoming Pickings’ & ‘Delivery Pickings’ records using ‘Incoming Pickings’ & ‘Delivery Pickings’ menu.
    - For more details please check below screenshots and watch the video.
    """,
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'www.probuse.com',
    'depends' : [
        'cloth_tailor_management_odoo',
        'stock'
    ],
    'support': 'contact@probuse.com',
    'data' : [
        'views/cloth_request_details_view.xml',
        'views/stock_picking_view.xml',
        'views/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
