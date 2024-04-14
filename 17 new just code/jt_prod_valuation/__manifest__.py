# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-Today Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Anil R. Kesariya(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Product Valuation',
    'summary': 'Get the valuation of your product based on specific lot/serial number.',
    'description': 'Get the valuation of your product based on specific lot/serial number.',
    'version': '17.0.0.1.0',
    'category': 'Inventory/Purchase',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'depends': ['purchase', 'sale_management', 'stock_account'],
    'data': [
        'views/inventory_valuation_view.xml',
        'views/product_template_inherit.xml',
        'views/product_product_inherit.xml',
    ],
     'images': ['static/description/poster_image.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 249.00,
    'currency': 'USD',
    'license': 'OPL-1',
}
