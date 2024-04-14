# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright © 2016 Techspawn Solutions. (<http://techspawn.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Warehouse Restrictions",

    'summary': """
    Warehouse Restriction,Stock Location Restrictions,Set warehouseman,Limit warehouse Operation Type To User.""",

    'description': """
        This Module Restricts the User from Accessing Warehouse and Process Stock Moves other than allowed to Warehouses and Stock Locations.
    """,
    'price':100,
    'currency': 'USD',
    'author': "Techspawn Solutions Pvt Ltd",
    'website': "http://www.techspawn.com",
    'license':'OPL-1',	
    'category': 'Warehouse',
    'version': '17.0.0.1',
    'images': ['static/description/Warehouse-Restrictionsv17.gif'],
    'depends': ['base', 'stock','sale_stock','sale_management','contacts'],

    'data': [
        'security/security.xml',
        'data/data.xml',
        'views/users_view.xml',
    ],
}
