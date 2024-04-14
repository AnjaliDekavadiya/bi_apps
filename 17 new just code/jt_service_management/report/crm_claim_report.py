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

from odoo import fields, models, api, tools

AVAILABLE_PRIORITIES = [
   ('0', 'Low'),
   ('1', 'Normal'),
   ('2', 'High')
]

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


class CRMClaimReport(models.Model):
    """ CRM Claim Report"""

    _name = "crm.claim.report"
    _auto = False
    _description = "CRM Claim Report"

    team_id = fields.Many2one('crm.team', 'Team', readonly=True) #, oldname='section_id'
    nbr = fields.Integer('# of Claims', readonly=True)  # TDE FIXME master: rename into nbr_claims
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    claim_date = fields.Datetime('Claim Date', readonly=True)
    delay_close = fields.Float('Delay to close', digits=(16, 2), readonly=True, group_operator="avg",
                               help="Number of Days to close the case")
    stage = fields.Selection(STAGES, 'Stage', readonly=True, domain="[('team_ids', '=', team_id)]")
    categ_id = fields.Many2one('crm.claim.category', 'Category', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priority')
    date_closed = fields.Datetime('Close Date', readonly=True)
    date_deadline = fields.Date('Deadline', readonly=True)
    delay_expected = fields.Float('Overpassed Deadline', digits=(16, 2), readonly=True, group_operator="avg")
    email = fields.Integer('# Emails', readonly=True)
    subject = fields.Char('Claim Subject', readonly=True)
    create_date = fields.Date("Create Date", readonly=True)

    def init(self):
        """ Display Number of cases And Team Name
        @param cr: the current row, from the database cursor,
         """
        cr = self._cr
        tools.drop_view_if_exists(cr, 'crm_claim_report')
        cr.execute("""
            create or replace view crm_claim_report as (
                select
                    min(c.id) as id,
                    c.date as claim_date,
                    c.date_closed as date_closed,
                    c.date_deadline as date_deadline,
                    c.stage,
                    c.team_id,
                    c.partner_id,
                    c.company_id,
                    c.categ_id,
                    c.name as subject,
                    count(*) as nbr,
                    c.priority as priority,
                    c.create_date as create_date,
                    avg(extract('epoch' from (c.date_closed-c.create_date)))/(3600*24) as  delay_close,
                    (SELECT count(id) FROM mail_message WHERE model='crm.claim' AND res_id=c.id) AS email,
                    extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24) as  delay_expected
                from
                    crm_claim c
                group by c.date,
                        c.team_id, c.stage,
                        c.categ_id, c.partner_id, c.company_id, c.create_date,
                        c.priority, c.date_deadline, c.date_closed, c.id
            )""")
