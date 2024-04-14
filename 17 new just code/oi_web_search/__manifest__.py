{
    "name": "Advance Search",
    "summary": "Advanced Search, List View Search, List View Manager, Global Search, Quick Search, Listview Search, Search Engine, Advance Search, Advance Filter, Field Search, Advance Search Tree",
    "version": "17.0.1.1.14",
    "category": "Extra Tools",
    "website": "https://www.open-inside.com",
    "description": """
        
    """,
    "website": "https://www.open-inside.com",
    "author": "Openinside",
    "license": "OPL-1",
    "price" : 85,
    "currency": 'USD',    
   
    "installable": True,
    # any module necessary for this one to work correctly
    "depends": [
       'web', 'oi_web_selection_tags'
    ],

    # always loaded
    'data': [
       
    ],
    'assets': {
        'web.assets_backend': [
            "oi_web_search/static/src/css/style.scss",
            'oi_web_search/static/src/search_menu/search_menu.js',
            'oi_web_search/static/src/search_menu/search_menu.xml',
            'oi_web_search/static/src/search_bar/search_bar.xml',
            'oi_web_search/static/src/search_bar/search_bar.js',
            "oi_web_search/static/src/many2many_tags/many2many_tags.js",
            "oi_web_search/static/src/search/search_model.js"
            ],
        },        
    'images' : [
        'static/description/cover.png'
        ],      
    'odoo-apps' : True 
}