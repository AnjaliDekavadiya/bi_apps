# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	"name" : "Internal Transfer and Receipts Backdate-Remarks in Odoo",
	"version" : "17.0.0.0",
	"category" : "Warehouse",
     'summary': 'Internal Transfer backdate purchase receipt backdate transfer backdating stock backdate remarks purchase accounting backdate purchase transfer backdate stock operation backdate inventory backdate stock back-date stock transfer shipment backdate receipt',
     "description": """
     
     odoo internal transfer backdate internal transfer remarks internal transfer backdate and remarks,
     odoo receipt backdate receipt remarks receipt backdate and remarks,
     odoo internal transfer and receipt backdate internal transfer and receipt remarks,
     odoo internal transfer and receipt backdate and remarks,

     odoo stock transfer backdating stock transfers backdating inventory stock transfer backdating
     odoo inventory transfer backdating inventory transfer backdating
     odoo stock backdate Stock Transfers Backdate inventory Transfers Backdate
     odoo inventory backdating option stock backdating options Inventory Backdate Operations
     odoo Backdate Options backdating options Inventory Backdate Operations Backdate Operations
     odoo warehouse backdate operations warehouse stock backdate operations
     odoo stock backdate odoo stock remarks transfer remarks warehouse delivery remarks warehouse remarks
     odoo inventory remarks odoo stock backdate remarks
     odoo stock accounting backdate transfer backdate on stock odoo


     odoo stock transfer back dating stock transfers back dating inventory stock transfer back dating
     odoo inventory transfer back dating inventory transfer back dating odoo
     odoo stock back date Stock Transfers Back-date inventory Transfers Backdate
     odoo inventory back-dating option stock back dating options Inventory Back date Operations
     odoo Back-date Options back dating options Inventory Back date Operations Back date Operations
     odoo warehouse back date operations warehouse stock back date operations
     odoo stock back date odoo stock remarks transfer remarks warehouse delivery remarks warehouse remarks
     odoo inventory remarks odoo stock back date remarks
     odoo stock accounting back date transfer back date on inventory odoo

     odoo receipt back dating stock receipt back dating purchase receipt back dating
     odoo purchase receipt transfer back dating receipt back dating odoo
     odoo stock receipt back date receipts Back-date purchase receipt Back date
     odoo purchase receipt back-dating option receipt back dating options receipt Back date Operations
     odoo receipt Back-date Options receipt back dating options receipt Back date Operations Back date Operations receipt
     odoo receipt back date operations receipt stock back date operations
     odoo receipt back date odoo receipt remarks transfer remarks receipt delivery remarks receipt remarks
     odoo receipt remarks odoo stock receipt back date remarks
     odoo purchase receipt accounting back date transfer back date on receipt odoo

     odoo Internal Transfer back dating stock Internal Transfer back dating Internal Transfer back dating
     odoo stock Internal Transfer back dating Internal Transfer back dating odoo
     odoo stock Internal Transfer back date Internal Transfers Back-date purchase Internal Transfers Back date
     odoo Internal Transfer back-dating option Internal Transfer back dating options Internal Transfer Back date Operations
     odoo Internal Transfer Back-date Options Internal Transfer back dating options Internal Transfers Back date Operations Back date Operations Internal Transfer
     odoo Internal Transfer back date operations Internal Transfers stock back date operations
     odoo Internal Transfer back date odoo Internal Transfer remarks Internal Transfer remarks Internal Transfer delivery remarks Internal Transfer remarks
     odoo Internal Transfer remarks odoo stock Internal Transfer back date remarks
     odoo stock Internal Transfer accounting back date Internal Transfer back date on Internal Transfer odoo

     odoo delivery backdating stock delivery backdating delivery transfer backdating
     odoo delivery order backdating delivery transfer backdating
     odoo delivery order backdate delivery order Backdate delivery Transfers Backdate
     odoo delivery backdating option delivery backdating options delivery operation Backdate on delivery order
     odoo Backdate Options backdating options delivery order Backdate Operations Backdate Operations for delivery
     odoo warehouse delivery order backdate operations delivery order backdate operations
     odoo delivery backdate odoo delivery remarks delivery order remarks delivery remarks stock delivery remarks
     odoo delivery process remarks odoo delivery process backdate remarks
     odoo delivery accounting backdate delivery backdate on goods transfer odoo
     odoo Inventory Adjustment backdating Inventory Adjustments backdating inventory backdating
     odoo inventory stock backdating inventory back date
     odoo Inventory Adjustment backdate Inventory Adjustment Transfers Backdate Inventory Adjustment Backdate
     odoo Inventory Adjustments backdating option Inventory Adjustments backdating options Inventory Adjustments Backdate Operations
     odoo Backdate Options backdating options Inventory Adjustments Backdate Operations Backdate Operations on Inventory Adjustments
     odoo warehouse backdate operations warehouse stock backdate operations
     odoo stock Inventory backdate odoo stock Inventory Adjustment remarks Inventory Adjustments remarks warehouseInventory Adjustments remarks
     odoo opening inventory remarks odoo Inventory Adjustment backdate remarks opening stock balance backdate
     odoo Inventory Adjustment accounting backdate Inventory Adjustments backdate on stock odoo


     odoo Inventory Adjustment back dating Inventory Adjustments back dating Inventory Adjustments back dating
     odoo Inventory Adjustment back dating Inventory Adjustments back dating odoo
     odoo Inventory Adjustments back date Inventory Adjustments Back-date Inventory Adjustment Back date
     odoo Inventory Adjustment back-dating option Inventory Adjustments back dating options Inventory Adjustment Back date Operations
     odoo Back-date Options back dating options Inventory Back date Operations Back date Operations
     odoo Inventory Adjustment back date operations Inventory Adjustments stock back date operations
     odoo Inventory Adjustment back date odoo Inventory Adjustment remarks transfer remarks Inventory Adjustments remarks warehouse remarks
     odoo Inventory Adjustment remarks odoo Inventory Adjustment back date remarks
     odoo Inventory Adjustment accounting back date Inventory Adjustment back date on inventory odoo

    
     entries so to avoid the problem this app will help to put custom back date and remarks.
     Custom back date will be transfer to stock entries and accounting entries  
     
     """,
	"author": "BrowseInfo",
	"website" : "https://www.browseinfo.com",
	"price": 18,
	"currency": 'EUR',
	"depends" : ['base','account','stock','purchase'],
	"data": [
			'security/ir.model.access.csv',
			'wizard/validate_internal.xml',
			'views/inherit_stock_picking.xml',
			],
    "license":'OPL-1',
	"auto_install": False,
	"installable": True,
	"live_test_url":'https://youtu.be/ygGDh74XwQs',
	"images":["static/description/Banner.gif"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
