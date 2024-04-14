# -*- coding: utf-8 -*-
{
    'name': "Kardex Valorizado Sunat 13.1",

    'summary': """
        Kardex Valorizado Formato Sunat 13.1""",

    'description': """
        Kardex por fecha y ubicación con costos unitarios con el formato solicitado
        por sunat 13.1 en excel.
    """,

    'author': "Codex Development",
    'website': "https://www.perucodex.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_accountant',
        'account_reports',
        'stock',
        'l10n_latam_invoice_document',
        'pc_l10n_pe_edi_stock_base',
        ],

    #Licence
    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/existence_type_sunat.xml',
        'views/product_template_views.xml',
        'wizard/kardex_sunat_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 359.99,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'sequence': 0,
}
