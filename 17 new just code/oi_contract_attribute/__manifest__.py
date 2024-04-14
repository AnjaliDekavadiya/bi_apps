# -*- coding: utf-8 -*-
# Copyright 2018 Openinside co. W.L.L.
{
    "name": "Employee Contract Attributes",
    "summary": "Employee Contract Attributes, Attributes for Employee Contracts, Contract Specifications, Employee, Payroll, Accounting, Multiple Allowances, Salary Rule, Salary Structure, Allowances, Deduction, HR, Human Resources",
    "version": "17.0.0.0.9",
    'category': 'Human Resources',
    "website": "https://www.open-inside.com",
	"description": """
		 Employee Contract Attributes
		 
    """,
	'images':[
        'static/description/cover.png'
	],
    "author": "Openinside",
    "license": "OPL-1",
    "price" : 29.99,
    "currency": 'USD',
    "installable": True,
    "depends": [
        'oi_hr_salary_schedule', 'oi_workflow'
    ],
    "data": [
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'data/hr_contract_type.xml',
        'view/hr_contract.xml',
        'view/hr_attribute.xml',
        'view/hr_attribute_value.xml',      
        'view/hr_attribute_value_approval.xml',  
        'view/hr_job.xml',
        'view/hr_contract_type.xml',
        'view/action.xml',
        'view/menu.xml',
        'security/ir.model.access.csv',
    ],
    'assets' : {
        'web.assets_backend' : [
            # 'oi_contract_attribute/static/src/js/attribute_selection_field.js',
            # 'oi_contract_attribute/static/src/js/attribute_many2one_field.js'
            ]        
    },
    'post_init_hook' : 'post_init_hook',
    'odoo-apps' : True    
}

