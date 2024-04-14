# -*- coding: utf-8 -*-

###################################################################################
# 
#   Odoo Proprietary License v1.0
# 
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have purchased a valid license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
# 
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
# 
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
# 
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
# 
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#
###################################################################################

{
    'name' : 'VKS Import Excel',
    'version': '17.0.1.0',
    'sequence': 981,
    'category': 'Tools',
    'summary': 'Optimize importing data from excel, especially import images and documents from URL or local file path, import employees, import customers, import products, import Lot/Serial Number, import Inventory Adjustments, import Bank Statement, import sales orders, import purchase orders, import pricelist, import invoices, import BOMs, import manufacturing routings, import Journal Entries, import timesheets, import project tasks, import working times, import work schedules, import manufacturing work orders, import analytic distribution',
    'author': 'Tuan Bui VKS',
    'website': 'https://www.youtube.com/watch?v=Auaqj6WtdcM&list=PLSKcWRTtEl5qzvRaI-VTGavfReiHS_EEb&index=5',
    'license': 'OPL-1',
    'price': 1250,
    'currency': 'USD',
    'depends' : [
        'base','web','base_import', 'mail', 'mail_bot'
    ],
    'live_test_url': 'https://www.youtube.com/watch?v=Auaqj6WtdcM&list=PLSKcWRTtEl5qzvRaI-VTGavfReiHS_EEb&index=5',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/base.xml',
        'views/manage_object_import.xml',
        'views/import_data.xml',
        'data/mail_data.xml',
        'data/vks_import_excel_initdata.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'assets': {
#         'web.assets_common': [
#             
#         ],
        'web.assets_backend': [
            'vks_import_excel/static/src/js/export_dialog.js',
            'vks_import_excel/static/src/js/list_controller.js',
            'vks_import_excel/static/src/js/import_render.js',
            'vks_import_excel/static/src/xml/export_button.xml'
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True
}
