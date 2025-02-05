{
    'name': 'SaaS-Tenant:SaaS Tenant',
    'version': '0.11',
    'category': 'SaaS',
    "summary": "Tenant Module",
    'license': 'OPL-1',
    'website': 'http://www.pragtech.co.in',
    'description': """Openerp SAAS Tenant Restriction Module """,
    'author': 'Pragmatic TechSoft Pvt. Ltd.',
    'depends': ['base', 'sales_team','web'],
    'data': [
        'security/saas_service_security.xml',
        'views/openerp_saas_tenant_view.xml',
        'views/users_view.xml',
        # 'ir_actions_view.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/res_config_view.xml',
        # 'static/src/xml/template.xml',
        # 'views/tenant_dashboard.xml',
        'wizards/db_space_exceeded_wizard.xml',

    ],
    'assets': {
        'web.assets_backend': [
            # "openerp_saas_tenant/static/src/xml/dashboard.xml",
            "openerp_saas_tenant/static/src/js/main.js",
            "https://www.gstatic.com/charts/loader.js",
            
        ],
        # 'web.assets_qweb': [
        #     'openerp_saas_tenant/static/src/xml/template.xml',
        # ],
    },
    'installable': True,
    'active': False,
}
