# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    'name': 'HR Employee Entry Checklist',
    'version': '1.0.1',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'category': 'Human Resources Management',
    'summary': 'Employee Entry checklist',
    'description': """Manage Entry checklist on Employees
    Entry Checklist
    Employee Checklist
    Employee Entry Checklist
    Employee Exit Checklist
    Hiring Procedure
    Entry Process
    Eployee Data Details
    """,
    'depends': ['hr'],
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'data': [
        "security/ir.model.access.csv",
        "views/employee_view.xml",
    ],
    'images': [
        'static/description/employee_checklist_cover_almightycs.jpg',
    ],
    'sequence': 1,
    'application': False,
    'price': 12,
    'currency': 'USD',
}
