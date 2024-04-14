# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LockSupportTicketWizard(models.TransientModel):
    _name = 'lock.support.ticket.wizard'
    _description = 'Lock Support Ticket Wizard'
    
    
    start_date = fields.Datetime(
        string='Lock Start Date',
        default=fields.Datetime.now(),
    )
    end_date = fields.Datetime(
        string='Lock End Date',
    )
    lock_confirmation = fields.Boolean(
        string='Are You Sure?',
    )
    
    # @api.multi #odoo13
    def action_lock_ticket(self):
        if self.lock_confirmation != True:
            raise ValidationError("You are not sure so you can not lock ticket.")
        else:
            support_ticket_obj = self.env['helpdesk.support']
            support_ticket = support_ticket_obj.browse(self._context.get('active_id'))
#             support_ticket.lock_start_date = self.start_date
            support_ticket.write({'lock_start_date':self.start_date,
                                  'lock_end_date':self.end_date,
                                  'locked_user_id':self.env.uid,
                                  'is_helpdesk_locked':True,
                                  })
#             support_ticket.lock_end_date = self.end_date
#             support_ticket.locked_user_id = self.env.uid
#             support_ticket.is_helpdesk_locked = True
