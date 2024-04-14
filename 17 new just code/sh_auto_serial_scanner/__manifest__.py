# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Lot/Serial Number Barcode Scanner",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "0.0.1",
    "category": "Warehouse",
    "summary": "Automatic Scan Lot Barcode Scanner Scan And Add Barcode Of Serial Number Scan Shipment Barcode Lot Scan Serial Scan Add Shipment Barcode Scan Incoming Order Barcode Add Delivery Order Barcode Serial Number Scanner Auto Add Barcode Odoo Lot Number Barcode Scanner Serial Numbers Barcode Scanner Lots Scanner Automatic Lot Numbers Add Auto Add Lot Auto Add Serial Scan Product With Serial Number Scan Product With Lot Number Scan Lot Number Scan Barcode Number Odoo",
    "description": """Are you still add Serial numbers/Lot numbers manually? then it is a time-consuming process. By default, In Odoo user has to scan and add barcode of Serial numbers/Lot numbers one by one. so it is a boring process. Here we made this process automated. This module allows you to scan and add products with Serial numbers/Lot numbers. It helps to manage the product Serial numbers/Lot numbers in the purchase(Incoming Order) process and sale(Delivery Order) process easily, so you can easily scan the barcode of Serial numbers/Lot numbers in Picking (Shipment/Delivery). scan it and you do! So be very quick in all operations of odoo and cheers!
 Lot/Serial Number Barcode Scanner Odoo""",
    "depends": ["barcodes", "stock"],
    "data": [
            "views/stock_move_views.xml",
    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": 80,
    "currency": "EUR",
    "license": "OPL-1"
}
