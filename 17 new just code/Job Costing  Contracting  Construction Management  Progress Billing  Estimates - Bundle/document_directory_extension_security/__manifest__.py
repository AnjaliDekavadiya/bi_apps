# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Document Management with Document Numerbing and Tags',
    'price': 129.0,
    'depends': ['document_directory_extension'],
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """Attachment/Document Extension with Directory Numerbing and Tags""",
    'description': """
Document Extension
Document Extension. This module add directory on ir.attachment model
Attachment/Document Extension with Directory and Numbering
Document Extension
Document Attachment
Attachment
Attachment/Document Extension with Directory and Numbering
This module will add below features to document/attachment module of Odoo.
1. Creation directory/folder by model/object.
2. Every directory/folder having separate sequence numbering for attachments.
3. Security on directory so only specific group can access/create document/attachment inside that directory. (Optional if you do not select group then no security).
4. Directory hiearchy view.
5. Document menu is only available for Document Manager group. (New group has been created for Document Manager).
6. This app is totally dedicated to Document Manager who manage document of ERP.
Available Menus:
document management system
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
dms
document management system
dms
Document
Document/Directories
Document/Directories/Directories
Document/Directories/Directories Structure
Document/Documents
Document/Documents/Documents
Directory Form View
document number
document sequence
document sequence
document numbering
document directory
document folder
folder
directory
* INHERIT Ir attachment.form (form)
* INHERIT Ir attachment.search (search)
* INHERIT Ir attachment.tree (tree)
document.directory form (form)
document.directory search (search)
document.directory tree (tree)
document.directory.hierarchy (tree)
attachment number
attach number
document attach number
document numbering
document number
number attachment
odoo document attachment number
filestore
file store
file number
files number
folder
full dms
dms
tags document
document tags
document number
document folders
attachment unique number
reference unique number
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/document_directory_extension_security/259',#'https://youtu.be/Q9P82N570Tc',
    'version': '4.24.2',
    'category' : 'Document Management',
    'data':[
        'security/document_security.xml',
        'security/ir.model.access.csv',
        'views/document_directory_tags.xml',
        'views/attachment_tags.xml',
        'views/document.xml',
        'views/attachment_directory.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}
