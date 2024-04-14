# -*- coding: utf-8 -*-
{
    'name': "Pc Edi Stock Base",

    'summary': """
        Stock Base module with especial fields""",

    'description': """
        Especial fields for picking with SUNAT data
    """,

    'author': "Codex Development",
    'website': "https://www.perucodex.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'stock',
        'l10n_pe',
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_latam_document_type_data.xml',
        'data/type_operation_sunat.xml',
        'views/stock_picking_views.xml',
    ],
}
