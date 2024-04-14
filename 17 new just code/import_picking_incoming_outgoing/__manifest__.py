# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
   'name': "Import Delivery Orders Incoming Shipments and Internal Tranfer",
   'version': '6.4',
   'category': 'Inventory/Inventory',
   'license': 'Other proprietary',
   'price': 29.0,
   'currency': 'EUR',
   'summary': """Allow you to Import Delivery Orders Incoming Shipments and Internal Tranfer Pickings from Excel""",
   'description':  """
This module allow you to import Incoming , Outgoing and Internal Transfer Picking from from excel file.
import delivery order
import picking
import stock picking
import incoming shipments
import transfere
delivery order import
delivery orders import
picking import
pickings import
incoming shipment import
import picking from excel

    """,
   'author': "Probuse Consulting Service Pvt. Ltd.",
   'website': "http://www.probuse.com",
   'support': 'contact@probuse.com',
   'images': ['static/description/itda.jpg'],
   'live_test_url': 'https://probuseappdemo.com/probuse_apps/import_picking_incoming_outgoing/479',#'https://youtu.be/-LLe-PKlBTc',
   #'live_test_url': 'https://youtu.be/dp7qAVct6OE',
   'external_dependencies': {'python': ['xlrd']},
   'depends': [
       'barcodes',
       'stock'
    ],
   'data': [
      'security/ir.model.access.csv',
      'wizard/picking_incoming_outgoing_view.xml',
    ],
    'installable' : True,
    'application' : False,
    
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
