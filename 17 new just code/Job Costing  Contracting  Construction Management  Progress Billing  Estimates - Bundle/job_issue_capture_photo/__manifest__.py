# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Scan & Capture Photo for Job_Task / Issue',
    'version': '8.1.2',
    'price': 49.0,
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """This app allow you to take photo from your mobile and save to job and issue.""",
    'description': """
scan
scan image
scan photo
photo scan
image scan
Capture photo
Capture image
load image
image
photos
images
photo
image
mobile photo
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
    'images': ['static/description/image.jpg'],
#    'live_test_url': 'https://youtu.be/HD0TfJDA4OQ',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/job_issue_capture_photo/700',#'https://youtu.be/OOXFyJRcts8',
    'depends': [
        'base_capture_photo',
        'construction_contracting_issue_tracking',
#        'issue_tracking_employee_portal'
    ],
    'data':[
        'views/project_task_view.xml',
        'views/construction_ticket_view.xml',
        'views/task_image_template_view.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
