# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Website Product Warranty And Policies',
    'version': '1.1',
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'category' : 'Website',
    'license': 'Other proprietary',
    'price': 20.0,
    'currency': 'EUR',
    'website': 'https://www.probuse.com',
    'description': ''' 
Product Warranty And Policies - E-Shop
This module allows to add product warranty and policies information on product screen of E-Shop at website. 

Features: 
1. Configure warranty and policies on product template form. 
2. Allow user to use existing warranty field on product form using that warranty information will be build and also allow to user to modify it. 

Notes: Currently (Odoo standard website_sale module) E-Shop showing static content of policies for all products which is shared by all E-Shop products. This module will remove that limitation and allow admin user to write product policies by each product. 
 ''',
    'depends':['website_sale'],
    'data' : [
          'views/product_view.xml',
          'views/template.xml'
              ],
    'installable':True,
    'auto_install':False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
