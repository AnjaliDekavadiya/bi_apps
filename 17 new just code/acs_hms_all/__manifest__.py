# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    'name': 'Hospital Management System (All HMS Modules BY AlmightyCS)',
    'summary': 'Hospital Management System having all HMS modules',
    'description': """
        all hms modules by hms acs hms AlmightyCS
        Hospital Management System Premium. acs hms hospital management system by almighty consulting services.
        hospital certificate and medical certification medical document management hospital barcode system insurance management system
        laboratory management system radiology and pathology management next patient screen, manage vitals signs 
        of patient in appointment and also details of all the physical examinations of patient.
    """,
    'version': '1.0.1',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': [
        'acs_hms_base',
        'acs_hms', 
        'acs_hms_barcode', 
        'acs_hms_certification',
        'acs_hms_dashboard',
        'acs_hms_hospitalization',
        'acs_document_base',
        'acs_documents_preview',
        'acs_hms_documents_preview',
        'acs_hms_insurance',
        'acs_hms_insurance_hospitalization',
        'acs_hms_insurance_laboratory',
        'acs_laboratory',
        'acs_hms_laboratory',
        'acs_hms_laboratory_hospitalization',
        'acs_hms_next_patient_screen',
        'acs_pharmacy',
        'acs_hms_pharmacy',
        'acs_hms_vaccination',
        'acs_hms_portal',
        'acs_certification',
        'acs_hms_commission',
        'facility_management',
        'acs_hms_online_appointment',
        'acs_hms_operation_theater',
        'acs_hms_icd10',
        'acs_hms_webcam',
        'acs_invoice_split',
        'acs_hms_insurance_radiology',
        'acs_radiology',
        'acs_hms_radiology',
        'acs_hms_radiology_hospitalization',
        #Extra Modules
        'acs_hms_blood_bank',
        'acs_hms_medical_representative',
        'acs_sms',
        'acs_hms_sms',
        'acs_hms_subscription',
        'acs_hms_subscription_physiotherapy',
        'acs_hms_ambulance',
        'acs_hms_video_call',
        'acs_whatsapp',
        'acs_whatsapp_meta',
        'acs_hms_whatsapp',
        'acs_pharmacy_whatsapp',
        'acs_laboratory_whatsapp',
        'acs_radiology_whatsapp',
        'acs_hms_rating',
        'acs_hms_nursing',
        'invoice_barcode',
        'invoice_with_stock_move',
        'acs_product_barcode_generator',
        'acs_consent_form',
        'acs_hms_consent_form',
        'acs_commission',
        'acs_hms_vital_examination',
        'acs_portal_user_image',
        'acs_invoice_summary',
        'acs_hms_invoice_summary',
        'web_timer_widget',
        'acs_hms_recurring_procedure',
        'acs_hms_pharmacy_pos',
        'acs_hms_survey',
        'acs_hms_insurance_surgery',
        'acs_hms_body_chart',
        'acs_website_booking',
        'acs_laboratory_website_booking',
        
        #Speciality Related Modules
        'acs_hms_aesthetic',
        'acs_hms_physiotherapy',
        'acs_hms_gynec',
        'acs_hms_paediatric',
        'acs_hms_ophthalmology',
        'acs_hms_dental',
        'acs_hms_dental_chart',
        'acs_hms_emergency',
        #Dashboard Modules
        'acs_hms_spreadsheet_dashboard',
    ],
    'data': [
    ],
    'images': [
        'static/description/hms_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 0,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: