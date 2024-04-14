# -*- coding: utf-8 -*-
{
    'name': "Dynamic Excel Report",

    'summary': """Dynamic & configurable excel report, Dynamic Excel Report Module, Global XLS Report, Export Excel Data, Export XLS Data, XLS Export, Export CSV, Output in Excel, Export Own Fields, XLSX Export, Easy create excel report from python code, Dynamic Excel Report, Excel Custom Template, XLS Custom Template, Excel Export, Excel Output, XLS Export, Export XLS, XLSX Export, Export Special Fields Odoo""",

    'description': """
        
    """,

    "author": "Openinside",
    "license": "OPL-1",
    'website': "https://www.open-inside.com",
    "price" : 27,
    "currency": 'USD',
    'category': 'Extra Tools',
    'version': "17.0.1.1.14",

    # any module necessary for this one to work correctly
    'depends': ['oi_excel_export'],
    
    'data' : [
        'security/ir.model.access.csv',
        'view/action.xml',
        'view/oi_excel_export_config.xml',
        'view/oi_excel_export_line.xml',
        'view/menu.xml'
        ],
    
    'odoo-apps' : True,
    'auto_install': True,
    'images':[
        'static/description/cover.png'
    ]     
}