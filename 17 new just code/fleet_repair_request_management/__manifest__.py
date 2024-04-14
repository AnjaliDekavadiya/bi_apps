# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Fleet/Auto/Vehicle Repair Service Scheduler, Online Request Management and Fleet Integration",
    'price': 89.0,
    'currency': 'EUR',
    # 'live_test_url': 'https://youtu.be/aLwVIxG0MLo',
    'live_test_url' : 'https://probuseappdemo.com/probuse_apps/fleet_repair_request_management/352',#'https://youtu.be/uoDR9d5Eihk',
    'license': 'Other proprietary',
    'summary': """This module allow you to manage online request from your customer for fleet/vehicle repair/service and integration with Odoo Fleet Module.""",
    'description': """
    Fleet Repair Request Management
    This module create fleet management request
Fleet/Auto/Vehicle Repair Service Scheduler, Request Management and Fleet Integration
Website Repair Request
Fleet Repair Request
Repair Request
customer Repair Request

General Workflow:
- Customer come on website and want to book fleet/auto/vehicle repair request.
- Customer go to link to create repair request.
- Customer can see form and fill details. (View Timeslots button allow him to see available time to meet Advisor/Representative).
- Customer can choose multiple services - Pricing are shown if price not avaiable on service form in backend then it will show 'Ask Advisor for Pricing'
- Cusotmer can choose Year, Make, Model and enter number plate / License Plate. (System will search License Plate in odoo list of fleets/vehicle and if found then it automatically link Vehicle in backend otherwise repair manager has to create new vehicle.).
- On submission of repair request system will create repair request in backend as well as create appoinment/meeting with advisor.
- Repair manager can open repair request in backend see detail entered by customer and also fill some details manually and assign that request to technicial or repair use. - Repair manager will create vehicle (if not available in system), service logs, repair order. - Repair user can work on repair request and fill timesheet.
- Repair manager can close request and that will send email to customer to request for feedback. - Customer can fill online feedback.
Repair
This module allow you to manage online request from your customer for fleet/vehicle repair/service and integration with Odoo Fleet.
Repair customer query
Repair customer help
Customer Repair request
Website Repair request
Website Repair request
Repair
Repair request system
Fleet Repair Request Management
unique Fleet Repair Request number to customer automatically
being able to reply to incoming emails to communicate with customer
unique Repair Request number per issue
print Repair Request

Attachment on website Repair Request
Message on website Repair Request
Add attchment
Add message
Send Message Repair Request
Attachment add Repair Request
Multiple attachments Repair Request
Add multiple attachments Repair Request
Add attachments on website
Website Fleet Repair Request

This module allow you manage your fleet repair request, repair request portal, billings for repair request, Timesheets.

Your Customer can send Repair request from your website and also attach documents.
Generation of unique Repair Request on submission and record it as Repair Request in backend.
Customer can check status of all Fleet Repair Request submitted by him/her on My Account page.
Print PDF - Fleet Repair Request
Repair User / Technician can communicate with customer using chatter and fill timesheet.
Repair Manager can close Repair Request and send repair feedback.
Customer can give feedback and rating of Fleet Repair Request.
Manage your fleet repair request using assignment to multiple repair teams.
Menus Available:
Fleet Repair
Fleet Repair/Analytic Account
Fleet Repair/Analytic Account/Analytic Accounts
Fleet Repair/Configuration
Fleet Repair/Configuration/Appointment Slots
Fleet Repair/Fleet Repair
Fleet Repair/Fleet Repair/Fleet Repair Request
Fleet Repair/Reports
Fleet Repair/Reports/Repair Analysis
Repair Users
Customer ===> Adrian
Repair Manager ==> Edward Foster
Repair User ==> Michel Fletcher
Schedule Service
Service Appointment Online Scheduler
Use this Online Form to Schedule Your Next Auto Repair & Car Service Appointment
Auto Repair
Car Service Appointment
Next Auto Repair
Schedule an Appointment With Us
bike Service Appointment
Customer ===> Adrian
Repair Manager ==>  Edward Foster
Repair User ==> Michel Fletcher
year
make
model
current mileage
mileage vehicle
vehicle repair
fleet repair
vehicle repair management
* INHERIT Portal My Fleet Repairs: project entries (qweb)
* INHERIT analytic.analytic.account.form (form)
* INHERIT calendar.event.form.view (form)
* INHERIT calendar.event.search.inherit (search)
* INHERIT ffleet.service.type.tree (tree)
* INHERIT fleet.vehicle.inherit.request (form)
* INHERIT fleet.vehicle.log.services.form (form)
* INHERIT mrp.repair (form)
* INHERIT my repairs: project menu entry (qweb)
* INHERIT res.partner form (form)
* INHERIT ticket form inherit (form)
* INHERIT website_date_info_assets (qweb)
* INHERIT website_fleet_repair_attachment (qweb)
Book Slot (qweb)
Contact us (qweb)
Contact us (qweb)
Contact us (qweb)
Dispaly Repiar (qweb)
Display Repair Requests (qweb)
Fleet Repair Request Genarate (qweb)
Fleet Repair Search (search)
Fleet form (form)
Fleet tree (tree)
Repair Calendar (calendar)
Repair Invalid (qweb)
Success Fleet (qweb)
Success Page (qweb)
Thanks (qweb)
Vehicle Service Wizard (form)
appointment.slot (search)
appointment.slot.form (form)
appointment.slot.tree (tree)
fleet kanban (kanban)
fleet team form (form)
fleet team tree (tree)
fleet.request.graph (graph)
fleet.request.pivot (pivot)
fleet_report (qweb)
Auto Repair Service Scheduler
Schedule Your Appointment in 4 Easy Steps
Fleet Repair Authorisation Platform
Cloud-based collaborative communication platform for fleet management, particularly for the automatic management of intervention authorisations by inspection, mechanical breakdown and tyre services, following business rules set by the company.
Faster and more efficient intervention
The workshop sends the authorisation to the company for evaluation.
The rules engine configured by the company analyses the data.
If the information is correct, automatic authorisation is issued. If not, the workshop user must contact the company to make the necessary changes.
Once the authorisation is approved, the process is closed and the intervention can be carried out on the vehicle.
mechanics 
brakes 
auto repair 
mechanic 
oil change     
automotive repair 
car service 
auto body 
car repair 
auto service 
transmissions 
auto mechanics 
auto shop
automotive service         
glass replacement             
windshield repair
repair windshield
auto shops
car repair service
auto repair service
auto repair and service
auto service and repair
vehicle repair
auto services
car auto repair
car repair services    
transmission problems
car maintenance
car shop
car repairs
auto repairs
engine repair
auto mechanic
brake repair
car shops
auto shop repair
automobile repair
oil change coupons        
auto maintenance        
auto repair shop
transmission repair
auto tech
auto repair services
truck repair
automotive mechanic
auto repair shops
windshield glass repair
transmission fluid change
auto repair mechanic
auto body shop
auto body shops
windshield auto glass replacement        
autoglass replacement
auto body parts
automotive maintenance
auto transmission
car problems
car air conditioning    
auto air conditioning
car window tinting
transmission service    
car mechanics
car mechanic
clutch repair
car window repair
car window replacement
car ac repair 
Based on the above, you want to determin wich of these keywords get searched the most when combined with your Geo Modifier / City attached to it:
USE “TIRES” AND “OIL CHANGE” TO RANK HIGHLY IN GOOGLE
TIRES
OIL CHANGE
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'version': '11.13.15',
    'category' : 'Services/Project',
    'depends': [
#                 'hr_timesheet_sheet',
                'project',
#                 'website_portal',
                'sales_team',
                'fleet',
#                'document', odoo13
                'repair',
                'calendar',
                'website',
                'hr_timesheet'
                ],
    'data':[
        'report/fleet_request_report.xml',
        'data/fleet_request_sequence.xml',
#        'data/feedback_template.xml', odoo13
        'views/fleet_thankyou_template.xml',
        'data/fleet_mail_template.xml',
        'security/repair_security.xml',
        'security/ir.model.access.csv',
        'wizard/vehicle_service_view.xml',
        'views/repair_report_view.xml',
        'views/fleet_repair_request_template.xml',
        'views/fleet_repair_view.xml',
        'views/hr_timesheet_sheet_fleet_view.xml',
        'views/my_fleet_repair_template.xml',
        'views/fleet_feedback_template.xml',
        'views/fleet_successfull_template.xml',
        'views/fleet_repair_team_view.xml',
        'views/project_view.xml',
        # 'views/fleet_thankyou_template.xml',
        'views/fleet_repair_attachment.xml',
        'views/fleet_vehicle_view.xml',
        'views/mrp_repair_views.xml',
        'views/analytic_account_view.xml',
        'report/fleet_repair_analysis.xml',
        'views/partner_view.xml',
        'views/appointment_slot_view.xml',
        'views/calendar_view.xml',
        'views/template_bookslot.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/fleet_repair_request_management/static/src/js/website_service_type.js',
        ],
    },
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
