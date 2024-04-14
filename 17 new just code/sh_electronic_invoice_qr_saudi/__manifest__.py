# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Electronic invoice KSA - Sale, Purchase, Invoice, Credit Note, Debit Note",
    'author': 'Softhealer Technologies',
    'website': 'https://www.softhealer.com',
    "support": "support@softhealer.com",
    'version': '0.0.1',
    'category': "Accounting",
    'summary': "Electronic invoice KSA Sale Saudi Electronic Invoice for Purchase Receipt Saudi VAT E-Invoice for Account QR Saudi VAT E Invoice for POS Electronic Invoice with QR code arabic translations ZATCA QR Code Saudi VAT Invoice Saudi E-Invoice all pos in one retail ksa retail saudi retail KSA saudi retail electronic saudi ksa saudi ksa electronic Odoo Saudi Invoice QR Code Invoice based on TLV Base64 string QR Code Saudi Electronic Invoice with Base64 TLV QRCode",
    'description': """This module allows you to print a Saudi electronic invoice with a QR code in the sale, purchase, invoice, credit note With Base64 TLV QR Code. You can display the data of VAT with tax details in the sale, purchase, invoice, credit note With Base64 TLV QR Code. You can print receipts in regional and global languages, such as Arabic and English As per Saudi Arabia Zakat's regulations to apply specific terms to the electronic invoice by 4th of Dec 2021.""",
    "depends" : ["account","base","sale_management","purchase","l10n_gcc_invoice"],
    "application" : True,
    "data" : [
            'security/ir.model.access.csv',
            'security/sh_electronic_invoice_qr_saudi_groups.xml',
            'data/sh_electronic_invoice_qr_saudi_paperformat.xml',
            'views/res_company_views.xml',
            'views/res_partner_views.xml',
            'views/account_move_views.xml',
            'report/account_invoice_report_templates.xml',
            'report/account_simplified_report_templates.xml',
            'report/account_move_report_action.xml',
            'report/invoice_external_layout_templates.xml',
            'views/sale_order_views.xml',
            'report/sale_order_report_templates.xml',
            'report/sale_order_proforma_report_templates.xml',
            'views/purchase_order_views.xml',
            'report/purchase_order_report_templates.xml',
            'views/product_product_views.xml',
            'views/product_template_views.xml',
            ],

    "external_dependencies": {
        "python": ["qrcode"],
    },

    'images': ['static/description/background.png', ],
    "license": "OPL-1",
    "auto_install":False,
    "installable" : True,
    "price": 55,
    "currency": "EUR"
}
