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

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class DiagnosisActionState(models.TransientModel):
    _name = 'diagnosis.action.state'
    _description = "Diagnosis Action state"

    action = fields.Selection([
        ('repaired', 'Repaired'),
        ('unrepairable', 'Unrepairable'),
        ('approval_required', 'Approval Required')
    ])

    def action_set_state(self):
        """
        This function changes ticket stage and its quote state based on diagnosis state.
        :return: Ticket stage and its quote state.
        """
        context = self.env.context
        ticket_id = context.get('ticket_id', False)
        if ticket_id:
            ticket = self.env['crm.claim'].browse(ticket_id)

            cause = ticket.cause
            action_type = ticket.action_type_id
            spare_parts = ticket.details_ids
            if self.action == 'repaired':

                if not action_type:
                    raise UserError(_('Please select Action taken'))

                if not cause:
                    raise UserError(_('Please Enter Description of Action taken'))

                if not ticket.quote_state:
                    ticket.write({'stage': 'repaired', 'quote_state': 'to_quote'})
                else:
                    ticket.write({'stage': 'repaired'})

            elif self.action == 'unrepairable':

                if not action_type:
                    raise UserError(_('Please select Action taken'))

                if not cause:
                    raise UserError(_('Please Enter Description of Action taken'))
                ticket.write({'stage': 'unrepairable', 'quote_state': 'not_quoted'})

            elif self.action == 'approval_required':
                if not spare_parts:
                    raise UserError(_('Please Enter Description of Action taken'))

                if not ticket.quote_state:
                    ticket.write({'stage': 'waiting_for_spares', 'quote_state': 'to_quote'})
                else:
                    ticket.write({'stage': 'waiting_for_spares'})
