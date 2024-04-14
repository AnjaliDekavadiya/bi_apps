# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################
{
    "name"          : "Website Loyalty Management Extension",
    "summary"       : """Loyalty Management Extension is a powerful tool that helps businesses create and
                            manage effective customer loyalty programs. It enhances the functionality of Loyalty
                            Management by adding new methods for granting loyalty points. The added loyalty
                            award basis allows you to define the desired value for each reward type from the
                            backend. It helps in customer retention and increased revenue, provides valuable data
                            insights, enhances brand advocacy, and allocates marketing resources efficiently.""",
    "author"        : "Webkul Software Pvt. Ltd.",
    "maintainer"    :  "Webkul Software Pvt. Ltd.",
    "depends"       : ['website_loyalty_management'],
    "category"      :  "website",
    "version"       :  "1.0.0",
    "sequence"      :  1,
    "license"       :  "Other proprietary",
    "website"       :  "https://store.webkul.com/odoo-loyalty-management-extension.html",
    "live_test_url" :  "https://odoodemo.webkul.com/?module=wk_loyalty_management_extension",
    "images"        :  ['static/description/banner.png'],
    "description"   :  """Optimize customer trust with Odoo Loyalty Management Extension which helps improve
                            the functionality of the website Loyalty management module.""",
    "data"          : [
                        'views/views_loyalty_management.xml',
                        'views/template.xml'
                    ],
    'assets'        : {
                        'web.assets_frontend': [
                            '/wk_loyalty_management_extension/static/src/js/loyalty.js',
                            
                        ],
                    },
    "application"   :  False,
    "installable"   :  True,
    "auto_install"  :  False,
    "currency"      :  "USD",
    "price"         :  100,
    "pre_init_hook" :  "pre_init_check",
}
