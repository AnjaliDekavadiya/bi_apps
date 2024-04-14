# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Sale Purchase Image And Sequence',
    'price': 30.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'version': '1.1.5',
    'category': 'Sales Management',
    'summary': """This module allows to add image and sequence number on sale order line and purchase order line and also on sale report and purchase report.
""",
    'description': ''' 
This module allows to add image and sequence number on sale order line and purchase order line and also on sale report and purchase report.
This module allow user to print product image and serial number on following reports: 
* Sales order report image
* Purchase order report image    

Report image serial number and sequence image. 
Tags:
product image
sale order image
sale order line image
product photo
sales order line image
line number
order line number
product image on order lines
sequence number on lines
purchase order image
purchase order line image
order line photo
show image on order line
report image
image report
show product image on report
show product photo on report
order line sequence number
order line counter

  ''',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'https://www.probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://youtu.be/BEZKdZucIFE',
    'depends':['sale', 'purchase'],
    'data' : [
              'views/sale_view.xml',
              'views/purchase_view.xml',
              'report/report_saleorder.xml',
              'report/report_purchasequotation.xml'
              ],
    'installable':True,
    'auto_install':False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
