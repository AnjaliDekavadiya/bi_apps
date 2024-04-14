# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'CRM Related Bundle Apps',
    'version': '3.0.0',
    'price': 9.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """CRM Related Bundle Apps""",
    'description': """
CRM Related Bundle Apps

    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/crmb.jpg'],
    'category' : 'Sales/CRM',
    'depends': [
           'crm_credit_note_refund',
           'mass_crm_pipeline_stage_update',
           'crm_timesheets_odoo',
           'quick_crm_opportunity_purchase',
           'unique_sequence_crm_opportunity',
           'print_crm_opportunity_activity',
           'material_requisition_crm_opportunity',
           'crm_opportunity_tendor',
           'crm_opportunity_task',
           'crm_opportunity_quotation',
           'crm_opportunity_purchase',
               ],
    'data':[
      
    ],
    'installable' : True,
    'application' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
