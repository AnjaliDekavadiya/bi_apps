{
    "name": "Salary Schedule",
    "summary": "Salary Schedule",    
    'category': 'Human Resources',
    "description": """
         
    """,
    
    "author": "Openinside",
    "license": "OPL-1",
    'website': "https://www.open-inside.com",
    "version": "17.0.0.0.7",
    "price" : 9.99,
    "currency": 'USD',
    "installable": True,
    "depends": [
        'hr_contract', 'oi_excel_export_dynamic'
    ],
    "data": [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'view/hr_salary_schedule.xml',
        'view/hr_salary_amount.xml',
        'view/hr_salary_grade.xml',
        'view/hr_job.xml',
        'view/hr_contract.xml',
        'view/action.xml',
        'view/menu.xml',
        'data/oi_excel_export_config.xml'
    ],
    'images': [
        'static/description/cover.png'
    ],
    'odoo-apps' : True      
}

