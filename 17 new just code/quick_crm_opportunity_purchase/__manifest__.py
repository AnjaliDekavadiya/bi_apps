# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quick Purchase Products from CRM',
    'version': '4.1.2',
    'currency': 'EUR',
    'price': 19.0,
    'license': 'Other proprietary',
    'category': 'Operations/Purchase',
    'summary': 'This module allow to add Purchase Products from CRM.',
    'description': """ 
This module allow to add Purchase Products from CRM .
quick crm purchase order
quick crm opportunity purchase
quick purchase order from crm
quick purchase order from opportunity
quick rfq opportunity
quick opportunity rfq
quick opportunity po
quick opportunity purchse
quick opportunity product
quick opportunity products
quick rfq produts
quick crm lead
quick crm purchse request
quick purchase request
quick team purchase
quick purchase team
quick sale_crm
quick crm
purchase module and crm module
Opportunity
Request for quotation Opportunity
Opportunity lines
product lines on Opportunity
crm quote
crm quote lines
customer product lines
create request for quotation from crm
sales team request for quotation
sales team products
linked to the generated purchase order
link purchase order with Opportunity
Opportunity on purchase order.
purchse order from Opportunity
create purchase order from Opportunity
rfq from Opportunity
create rfq from Opportunity
purchase order
rfq
crm extend
""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'depends': ['crm_opportunity_purchase'],
    'images': ['static/description/image.png'],
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/quick_crm_opportunity_purchase/106',#'https://youtu.be/Ecnl_N0Qp7s',
    'data': [
            'security/ir.model.access.csv',
            'wizard/create_rfq_view.xml',
            'views/opportunity_purchase_custom_view.xml',
             ],
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
