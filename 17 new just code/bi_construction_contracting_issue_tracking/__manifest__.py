{
    'name': "Job Contracting and Construction issue tracking system",
    'version': '17.0.0.0',
    'category': 'Projects',
    'summary': 'App manage contracting issue tracking for construction project issue Tracking for contracting issue tracking in construction job contracting issue system job costing issue Construction Job Costing issue Construction Material request Construction estimation',
    'description': """Construction & contracting issue tracking
	
	issue tracking in construction 
	project issue in construction 
	
	""",
    'author': "BrowseInfo",
    'website': 'https://www.browseinfo.com',
    'price': 19,
    'currency': 'EUR',
    'depends': ['base', 'sale_management', 'bi_material_purchase_requisitions', 'bi_odoo_job_costing_management',
                'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/email_temp.xml',
        'report/project_issue_report.xml',
        'report/proj_issue_report_view.xml',
        'views/issue_subject.xml',
        'views/issue_team.xml',
        'views/issue_type.xml',
        'views/issue_stages.xml',
        'views/configuration_view.xml',
        'views/issue_request_template.xml',
        'views/project_issues.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'bi_construction_contracting_issue_tracking/static/src/xml/**/*',
        ],
    },
    "auto_install": False,
    "installable": True,
    "live_test_url": 'https://youtu.be/iUGTm6Egh5w',
    "images": ["static/description/Banner.gif"],
    'license': 'OPL-1',
}
