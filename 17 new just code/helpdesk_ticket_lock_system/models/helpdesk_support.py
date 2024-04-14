# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'
    
    @api.depends()
    def _lock_duration(self):
        locked_date = datetime.strptime(self.locked_date,"%Y-%m-%d %H:%M:%S")
        lock_hour = locked_date + timedelta(hours=self.lock_duration)
        if lock_hour >= datetime.now():
            self.is_helpdesk_locked = True
            
        
    is_helpdesk_locked = fields.Boolean(
        string='Is Locked',
        readonly=True,
#         compute='compute_lock_ticket',
    )
    lock_start_date = fields.Datetime(
        string='Lock Start Date',
        readonly=True,
        tracking=True,
    )
    lock_end_date = fields.Datetime(
        string='Lock End Date',
        readonly=True,
        tracking=True,
    )
    locked_user_id = fields.Many2one(
        'res.users',
        string='Last Locked by',
        readonly=True,
        tracking=True,
    )
    unlock_user_id = fields.Many2one(
        'res.users',
        string='Last Unlocked By',
        readonly=True,
    )
#    lock_duration = fields.Integer(
#        'Lock Time',
#    )
    
    # @api.multi #odoo13
    def lock_ticket(self):
        self.locked_date = fields.Datetime.now()
        self.locked_user_id = self.env.uid
        
    # @api.multi #odoo13
    def action_unlock_ticket(self):
        if self.is_helpdesk_locked:
            self.unlock_user_id = self.env.uid
            self.is_helpdesk_locked = False
            self.lock_start_date = False
            self.lock_end_date = False
    
    # @api.multi #odoo13
    def write(self,vals):
#        lock_start_date =  vals.get('lock_start_date', False)
#        lock_end_date = vals.get('lock_end_date', False)
#        locked_user = vals.get('locked_user_id', False)
#        current_date = fields.Datetime.now()
#        pass_check = False
#        if vals.get('lock_start_date', False) and vals.get('lock_end_date', False):
#            pass_check = True
#            return super(HelpdeskSupport,self).write(vals)
#        if pass_check == False:
#            if not (current_date >= self.lock_start_date and current_date <= self.lock_end_date):
#                return super(HelpdeskSupport,self).write(vals)
#            if self.env.uid == self.locked_user_id.id:
#                return super(HelpdeskSupport,self).write(vals)
#            else:
#                raise ValidationError("You can not work on this ticket since ticket is locked by %s"%self.locked_user_id.name)
        if self.is_helpdesk_locked:
            if not (fields.Datetime.now() >= self.lock_start_date and fields.Datetime.now() <= self.lock_end_date):
                vals.update({'is_helpdesk_locked' : False})
                return super(HelpdeskSupport,self).write(vals)
                
            if self.env.uid == self.locked_user_id.id:
                return super(HelpdeskSupport,self).write(vals)
            else:
                raise ValidationError("You can not work on this ticket since ticket is locked by %s"%self.locked_user_id.name)
        else:
            return super(HelpdeskSupport,self).write(vals)
