# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
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
    'name': 'Repair Management',
    'version': '17.0.1.0.0',
    'category': 'Stock',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'https://www.jupical.com',
    'summary': "The complete Repair Management solution!",
    "license": "LGPL-3",
    'depends': ['stock_account','sale','stock', 'mrp', 'sale_management', 'purchase'],
    'data': [
        'security/crm_claim_pro_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'wizard/check_availability_wizard.xml',
        'wizard/add_ticket_to_existing_quot.xml',
        'wizard/spares_location_view.xml',
        'views/crm_claim_view.xml',
        'wizard/diagnosis_quotation_view.xml',
        'wizard/import_tickets_views.xml',
        'views/product_view.xml',
        'views/crm_claim_config_view.xml',
        'views/crm_claim_menu.xml',
        'report/crm_claim_report_view.xml',
        'views/crm_claim_data.xml',
        'views/crm_claim_sequence.xml',
        'views/ht_sale_view.xml',
        'views/res_company_view.xml',
        'views/email_notification.xml',
        'wizard/print_report_wizard.xml',
        'report/print_wizard_report_template.xml',
        'views/print_report_wizard_data.xml',
        'report/ticket_pivot_report_view.xml',
        'report/service_parts_report.xml',
        'views/daily_reminder_cron.xml',
        'views/service_center_reminder_temp.xml',
        'views/report_print_label.xml',
        'report/service_do_report_tem.xml',
        'views/service_do_report.xml',
        'views/purchase_order_view.xml',
        'views/stock_lot_view.xml',
        'views/menu.xml',
        # 'views/config_settings.xml'
        
    ],
    'installable': True,
    'application': True,
    'images': ['static/description/repair-managment.gif'],
    'currency': 'USD',
    'price': 499.00,
}
