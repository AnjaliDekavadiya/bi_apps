# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
{
    'name': "Advance Tender Management | Bid Management | Bid Evaluation | Tender Portal | Purchase Tender",
    'description': """
        - Tender Management
        - Bid Proposal
        - Bid Evaluation
        - Single tender for all product
        - Product wise tender
        - Purchase Tender
    """,
    'summary': """Advance Tender Management""",
    'version': "1.1",
    'author': 'TechKhedut Inc.',
    'company': 'TechKhedut Inc.',
    'maintainer': 'TechKhedut Inc.',
    'website': "https://www.techkhedut.com",
    'support': "info@techkhedut.com",
    'category': 'services',
    'depends': ['mail', 'purchase', 'product', 'stock', 'account', 'contacts', 'website'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/ir_cron.xml',
        'data/sequence.xml',
        'data/tender_data.xml',
        'data/tender_paper_format.xml',
        'data/website_menu.xml',
        # Wizard
        'wizard/bid_disqualify_view.xml',
        'wizard/bid_selection_view.xml',
        'wizard/tender_cancellation_reason_view.xml',
        'wizard/export_tender_line_view.xml',
        'wizard/import_tender_line_view.xml',
        # Views
        'views/assets.xml',
        'views/tender_info_view.xml',
        'views/tender_product_view.xml',
        'views/tender_configuration_view.xml',
        'views/tender_vendor_view.xml',
        'views/tender_bidding_view.xml',
        'views/tender_purchase_order_inherit.xml',
        'views/account_move_inherit_view.xml',
        'views/tender_web_template.xml',
        'views/res_config_view.xml',
        # Menus
        'views/menus.xml',
        # Reports
        'report/tender_bidding_report.xml',
        'report/tender_bidding_info_report.xml',

        # Mail Template
        'data/qualified_vendor_mail_template.xml',
        'data/bid_selection_mail_template.xml',
        'data/tender_cancellation_mail_template.xml',
        'data/multiple_vendor_bid_mail_template.xml',
        'data/vendor_signup_mail_template.xml',
        'data/website_edit_request_mail_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'tk_tender_management/static/src/xml/template.xml',
            'tk_tender_management/static/src/css/lib/dashboard.css',
            'tk_tender_management/static/src/css/lib/style.css',
            'tk_tender_management/static/src/css/style.scss',
            'tk_tender_management/static/src/js/tender_dashboard_owl.js',
        ],
        'web.assets_frontend': [
            'tk_tender_management/static/src/css/theme.css',
            'tk_tender_management/static/src/js/tender.js',
            'tk_tender_management/static/src/js/custom.js',
            'tk_tender_management/static/src/js/bootstrap-multiselect.js',
        ],
    },
    'images': [
        'static/description/cover.gif',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 299,
    'currency': 'USD',
}
