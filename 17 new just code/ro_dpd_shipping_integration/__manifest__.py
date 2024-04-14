# -*- coding: utf-8 -*-pack
{       # App information
        'name': 'DPD Romania Shipping Integration',
        'category': 'Website',
        'version': '1.0.0',
        'summary': """Shipping integration with Odoo is a crucial aspect of optimizing and streamlining business logistics. Odoo, a comprehensive business management software, allows seamless integration with various shipping carriers to enhance the efficiency of the shipping process. You can perform various operations like get Live shipping rate,Generate Shipping labels, Track Shipment,You can cancel the shipments too. You can find out our other modules like Vraja Shipping Integration, vraja technologies, vraja shipping, Romania shipping integration by vraja technologies, RO Shipping Integration, odoorodpd, odoo dpd, hungarygls, selfawb, odooselfawb.""",
        'description': """DPD Romania Shipping Integration""",
        # Dependencies
        'depends': ['delivery','stock','stock_delivery'],
        # Views
        'data':[
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/delivery_carrier.xml',
        'views/stock_picking.xml'],

        'images': ['static/description/cover.jpg'],

        'author': 'Vraja Technologies',
        'maintainer': 'Vraja Technologies',
        'website':'www.vrajatechnologies.com',
        'demo': [],
        'installable': True,
        'application': True,
        'auto_install': False,
        'price': '199',
        'currency': 'EUR',
        'license': 'OPL-1',
}
#12.0.30.09.2021 Initial Version
#15.0.14.03.22 add cancel functionality and make some changes like add parcel ids in parcel id field
