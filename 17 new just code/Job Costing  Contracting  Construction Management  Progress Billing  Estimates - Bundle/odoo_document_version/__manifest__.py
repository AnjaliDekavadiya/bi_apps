# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Document Version / Attachment Version',
    'price': 99.0,
    'version': '8.0.2',
    'depends': [
#        'document',
        'mail'
    ],
    'category' : 'Document Management',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """This app allow you to have document version on attachment records.""",
    'description': """
This module will add below feature:
document versioning
versioning
attachment versioning
versioning document
versioning attachment
versioning file
file versioning
doc versioning
new version
versioning file
dms
File Versions
Version History
document version control
version control
Versioning File System
DOCUMENT VERSION CONTROL
Document versions
Document Version Numbers
Document version control
version control
document management system
document file versioning
file version
Auto update version of attachment
Option to restrict auto versioning for attachment for specific models
Download version wise attachments
document version
version
version document
attachment version
version attachment
Document Extension
alfresco
document number
document sequence
document sequence
document numbering
document directory
document folder
filestore
file store
file number
files number
folder
document folders
attachment unique number
reference unique number
my documents
document tags
directory tags
dms
alfresco similar
document number
diretory number
file number
file sequence
document search
file store
filestore
Document Attachment


    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/odoo_document_version/133',#'https://youtu.be/w-8cHzWkVYw', #'https://youtu.be/Jpnja0KNcqw',
    'data':[
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/ir_attachement_view.xml',
        'views/res_model_versioning_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
