# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Agriculture - Bundle',
    'version': '5.1.5',
    'category' : 'Services/Project',
    'license': 'Other proprietary',
    'price': 1.0,
    'currency': 'EUR',
    'summary': """Odoo Agriculture - Bundle""",
    'description': """
Agriculture app
Agriculture Management
Crop Requests
Crops
Scouting
crop Agriculture
crop Scouting
Scouting
Scoutings
Scouting form
odoo Scouting
crop
Agriculture Management Software
Incidents
Dieases Cures
agribusiness
crop yield
agriculture institutes
Farmers
AMS
Farm Locations
farmers
farmer
Agriculture odoo
odoo Agriculture
Agriculture Management System
Animals
print Crop Requests Report
print Crops Report
odoo Agriculture Management Software
Farm Management Software
       
    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/afba.jpg'],
#     'live_test_url': 'https://youtu.be/TDPhPz_n83g',
    'depends': [
              'odoo_agriculture',
              'odoo_agriculture_website',
              'odoo_agriculture_ecommerce',
              'agriculture_job_cost_sheet',
              'agriculture_production_mrp',
              'agriculture_crop_scouting',
              'agriculture_weather_records',
              'agriculture_material_requisition',
              'agriculture_equipment_maintenance'
                ],
    'data':[
            ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
