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

from odoo import fields, models, tools

STAGES = [
    ('new', 'New'),
    ('logged', 'Assigned'),
    ('in_diagnosis', 'In Diagnosis'),
    ('diagnosed', 'Diagnosed'),
    ('waiting_for_spares', 'Waiting Confirmation'),
    ('repaired', 'Repaired'),
    ('unrepairable', 'Unrepairable'),
    ('ready_for_collection', 'Ready for Collection'),
    ('collected', 'Collected'),
]


class TicketPivotReport(models.Model):
    """ Ticket Analysis """
    _name = "ticket.pivot.report"
    _auto = False
    _description = "Ticket Analysis"
    _rec_name = 'id'

    date = fields.Datetime('Ticket Date', readonly=True)
    ready_collection_date = fields.Datetime('Ready for Collection Date', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    service_engineer_id = fields.Many2one('res.users', 'Service Engineer', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_brand_id = fields.Many2one('product.brand', 'Product Brand', readonly=True)
    service_center_id = fields.Many2one('service.center', 'Service Center', readonly=True)
    categ_id = fields.Many2one('crm.claim.category', 'Category', readonly=True)
    action_type_id = fields.Many2one('service.action.type', 'Action Type', readonly=True)
    stage = fields.Selection(STAGES, string='Stage')
    partner_company_id = fields.Many2one('res.partner', string='Partner Company', readonly=True)
    number_of_day = fields.Integer('Number of days from Ticket Created to Ready for collection', readonly=True)
    name = fields.Char('Ticket Number', readonly=True)

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'ticket_pivot_report')
        cr.execute("""
            CREATE OR REPLACE VIEW ticket_pivot_report AS (
                SELECT
                    t.id,
                    t.name,
                    t.date,
                    t.ready_collection_date,
                    t.company_id,
                    t.partner_id,
                    t.service_engineer_id,
                    t.product_id,
                    t.product_brand_id,
                    t.service_center_id,
                    t.categ_id,
                    t.action_type_id,
                    (SELECT parent_id FROM res_partner WHERE id = t.partner_id) AS partner_company_id,
                    (SELECT t.ready_collection_date::date - t.date::date) AS number_of_day,
                    t.stage
                FROM
                    crm_claim t
            )""")
