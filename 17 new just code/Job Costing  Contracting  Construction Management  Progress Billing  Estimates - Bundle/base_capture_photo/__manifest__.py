# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Base Scan and Upload Images on My Account Portal',
    'version': '5.1.4',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'price': 49.0,
    'currency': 'EUR',
    'summary': """Base Framework Module For Scan and Upload Images on My Account Portal""",
    'description': """
scan
scan image
scan photo
photo scan
image scan
photo
image
upload photo
upload image
photo upload
photo download
Scan and Upload Images for records
Uploaded Images Stored As Attachments and Also Chatter
Preview of Submitted Images

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': [
        'static/description/bcp.jpg'
    ],
    'depends': [
        'portal',
        'website'
    ],
    'data':[
        'views/snap_image_template_view.xml',
    ],
    'assets': {
            'web.assets_frontend': [
                'base_capture_photo/static/src/js/snap_image.js',
        ],
    },
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
