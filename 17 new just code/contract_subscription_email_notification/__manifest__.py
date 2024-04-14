# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Contract Subscription Email Notification and Reminder',
    'version': "5.1.6",
    'license': 'Other proprietary',
    'price' : 99.0,
    'support': 'contact@probuse.com',
    'currency': 'EUR',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/contract_subscription_email_notification/813',#'https://youtu.be/shqPUKh55WI',
    'category': 'Sales',
    'summary': 'Send email notification to customer when contract get in progress, expire soon and expired.',
    'description': """
    Contract Subscription
            """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': [
            'contract_recurring_invoice_analytic'
    ],
    'data': [
            'data/contract_subscription_cron.xml',
            # 'data/contract_subscription_mail_template.xml',
            'data/contract_subscription_mail_template_new.xml',
            'views/analytic_account_view.xml'
    ],
    'images': ['static/description/image.png'],
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
