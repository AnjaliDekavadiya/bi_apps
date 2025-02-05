# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Crop Scouting for Agriculture',
    'price': 49.0,
    'version': '7.1.6',
    'category' : 'Services/Projects',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """ This app add feature of Crop Scouting for Agriculture""",
    'description': """ 
Agriculture 
Crop Requests
Crops
Scouting
crop Agriculture
crop Scouting
Scouting
Scoutings
Scouting form
odoo Scouting
Soil
Weather
Insects
Agriculture app
Agriculture Management
Crop Requests
Crops
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
Dieases
Weeds
Plant Population
Print Crop Scouting Report

""",
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/agriculture_crop_scouting/435',#'https://youtu.be/Rw0opahBIg0',
    'depends': [
               'odoo_agriculture',
    ],
    'data': [
            'security/agriculture_scouting_security.xml',
            'security/ir.model.access.csv',
            'data/ir_sequence_data.xml',
            'report/crop_scouting_report.xml',
            'views/crop_soil.xml',
            'views/crop_weather.xml',
            'views/farmer_crop_request.xml',
            # 'views/crop_scouting.xml',
            'views/crop_scouting_new.xml',
            'views/crop_insects_view.xml',
            'views/crop_weeds_view.xml',
            'views/crop_plant_population_view.xml',
            'views/crop_dieases_view.xml',
            'views/crop_view.xml',
            'views/insects_view.xml',
            'views/weeds_view.xml',
            'views/dieases_view.xml',
            'views/plant_population_view.xml',
            'views/crop_wind_view.xml',
            'views/crop_air_temperature_view.xml',
            'views/crop_cloud_cover_view.xml',
            'views/menu_item.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

