# -*- coding: utf-8 -*-

{
    'name': 'Report Utils',
    'version': '1.2',
    'summary': """""",
    'description': """""",
    'category': 'Base',
    'author': 'bisolv',
    'website': "www.bisolv.com",
    'license': 'AGPL-3',

    'price': 35.0,
    'currency': 'USD',

    'depends': ['base'],

    'data': [
        'data/designs.xml',
        'data/date_format.xml',
        'data/header_section_orders.xml',
        'data/logo_styles.xml',
        'data/range_items.xml',
        'data/letter_cases.xml',
        'data/font_weight.xml',
        'data/layouts.xml',
        'data/direction.xml',
        'data/alignments.xml',
        'data/row_col_types.xml',
        'security/ir.model.access.csv',
        'views/reporting_template.xml',
        'report/standard_header.xml',
        'report/standard_footer.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}

