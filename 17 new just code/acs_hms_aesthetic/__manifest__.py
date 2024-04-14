# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name': 'Hospital Management System for Aesthetic',
    'version': '1.0.2',
    'summary': 'Hospital Management System for Aesthetic By AlmightyCS',
    'description': """
        Hospital Management System for Aesthetic. Aesthetic management system for hospitals
        With this module you can manage Aesthetic Patients acs hms almightycs dentist
    """,
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['acs_hms_portal', 'acs_documents_preview'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/aesthetic_wish_report.xml',
        'report/aesthetic_history_report.xml',
        'report/aesthetic_phototype_report.xml',
        'views/hms_aesthetic_base_view.xml',
        'views/acs_patient_view.xml',
        'views/acs_hms_views.xml',
        'views/hms_aesthetic_wish_view.xml',
        'views/portal_aestheticwish.xml',
        'views/portal_patient_history.xml',
        'views/portal_aesthetic_phototype.xml',
        'views/menu_item.xml',
    ],
    'images': [
        'static/description/acs_hms_aesthetic_almightycs_cover.png',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
    'price': 101,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
