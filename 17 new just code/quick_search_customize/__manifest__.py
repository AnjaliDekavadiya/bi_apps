# -*- coding: utf-8 -*-
{
    "name": "Advance Search & Quick Search",
    "version": "1.0",
    "category": "Extra Tools",
    "summary": "Search on top of list view with your own customization fields. Advance Search, Advanced Search, List View Search, List View Manager, Global Search, Quick Search, Listview Search, Search Engine, Advance Filter, Advanced Filter, Field Search, Tree Search, Search Expand, Powerful Search, Search List View, Best Search List, Search List, Search Tree, Tree Search, Tree View Search, Search Range, Search by Range, Search by Date, Searchbar, Web List Search, Search on List, Easy Search, Fast Search, Search for x2x, Search x2x, Visible Search, Search Filter, Multi Search, Multiple Search, Fastest Search, Base Search, Voraussuche, Recherche Avancée, Chercher, Søke, Buscar, Zoeken, поиск, Dynamic Search, Search View, Domain Filter, Code Search, Odoo Smart Search, Elastic Search, Speed Search, Elasticsearch, Search Suggestion, Search Keyword, Dynamic Filter, Product Search, Search Autocomplete, Auto Search, Automatic Search, Configure Search, Quick Product Search, Optimize Search, Better Search, Linear Search, Binary Search, Sequential Search, Interval Search, Interpolation Search, Search Algorithm, Odoo Advance Search, Odoo Quick Search, Odoo Advanced Search, Configurable Search.",
    "description": """
Allows advanced search on top of list view. This module allows one to customize own search columns for each model.
    """,
    "author": "Ivan Yang",
    "support": "ivan.yangkaivan@gmail.com",
    "maintainer": "Ivan Yang",
    "depends": [],
    "data": [
        "data/quick_search_data.xml",
        "security/quick_search_security.xml",
        "security/ir.model.access.csv",
        "views/quick_search_views.xml",
        "views/res_config_settings_views.xml"
    ],
    "images": ["static/description/banner.gif"],
    "assets": {
        "web.assets_backend": [
            "quick_search_customize/static/src/css/quick_search_customize.css",
            "quick_search_customize/static/src/views/quick_search_customize.js",
            "quick_search_customize/static/src/views/quick_search_customize.xml"
        ]
    },
    "license": "OPL-1",
    "price": 72.00,
    "currency": "EUR",
    "demo": [],
    "live_test_url": "http://52.221.105.67:7080/web?db=MODULE_QS13"
}