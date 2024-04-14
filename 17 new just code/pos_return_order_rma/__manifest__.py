# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'RMA for Point of Sales (POS)',
    'version': '5.2.3',
    'price': 49.0,
    'depends': [
                'website_portal_pos_orders',
                'website_shop_return_rma',
                'machine_repair_management',
                'website_request_return_rma_odoo',
                ],

    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Point of Sales Return Merchandise Authorization (RMA)""",
    'description': """
        Point of Sales (POS) RMA Management
        Return Material Authorization Management [RMA] for POS
        Repair - Scrap - Replacement for Return Order Management for POS
        Point of Sales RMA Return Merchandise Authorization
        Return Merchandise Authorization (RMA) Management Odoo App
        Your customer can go to the POS Order in Portal My Account of your website and create an RMA request. Customers can create an RMA return order by logging into Portal / My Account as shown.
        Allow your team to manage Return Material Authorization requests in the backend. Customers can go to the POS order list view and click the "Create RMA" button to return an item which will generate a return order (RMA Order) in the backend.
        Customers can see the list of RMA orders in Portal / My Account of your website.
        Allow your customer to specify the return reason during creation of RMA for POS order.
        We have added workflow on return order in backend (Draft -> Confirm -> Approve -> Return). Allow your stock inventory team to do return pickings from delivery orders (Odoo Standard Feature) using the return button on the delivery order picking of POS. It allows your customer to make multiple products/items on RMA order requests from the website.
        Before confirming, allow your team to select methods on Return Material Authorization Lines.
        Allow the manager to approve the Return Material Authorization confirmed request.
        Allow the team to create repair orders directly from the Return Material Authorization form.
        Print Return Material Authorization in pdf format as shown.
        Send by email Return Material Authorization to the customer as shown.
        Pos Order form has reference of Return Material Authorization RMA.
        Customer form has reference of all Return Material Authorization orders belonging to them.
        System makes a link up of RMA order with POS order as shown below screenshots.
        On the customer form a smart button showing all return RMA orders related to that customer.
        Print RMA PDF Report Print Return Report.
        Link Button "RMA Orders" My Account Portal on POS Order List View.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.jpg'],
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/pos_return_order_rma/375',#'https://youtu.be/d3svWb2qbjQ ',
    'category' : 'Sales/Point of Sale',
    'data':[
        'views/website_portal_sale.xml',
        'views/return_order_view.xml',
        'views/return_report.xml',
        'views/pos_order_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
