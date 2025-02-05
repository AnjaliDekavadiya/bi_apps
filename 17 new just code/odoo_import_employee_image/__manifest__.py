# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Import Employee Images from Excel (from Path and URL)",
    'version': '6.2.1',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to import employee images from excel using URL and Path.""",
    'description': """
This module help to import Employee from excel.
In this module for update Employee image you can add path as LOCAL PATH or URL also
In this module for import Employee you should create .xls or .xlsx,
Enter Employee name, Identification No and also image path of Employee image,
For Update Employee image or Employee image you should enter Employee name and image path.
Image path should be as "/home/downloads/.../*.jpg or .png or .jpeg etc." or "https://...." or "http://"
Import your Employee using your import file
Import Employee
Import Employee & Images
CSV Employee Images Import
Employee_image_upload
Employee_image_from_url
Import Employee Images From URL
import Employee
Employee import
Employee images
Employee image import
Employee image photos
Employee image load
Employee import csv
Employee import excel
image Employee
photo Employee
import Employee images
Employee images load odoo
odoo import load
Employee images upload
upload Employee image
upload Employee photo
import script Employee image
Employee load
Employee csv import image
Employee excel import image
image import Employee odoo
Employee csv image import    
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_import_employee_image/847',#'https://youtu.be/eg53z7iuVXA',
    'category' : 'Human Resources',
    'depends': [
        'hr',
    ],
    'data':[
        'security/ir.model.access.csv',
        'wizard/import_employee_image_xls_view.xml',
        'views/menu.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
