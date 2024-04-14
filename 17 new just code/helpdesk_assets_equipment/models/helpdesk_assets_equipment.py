# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime


class helpdeskAssetsEequipment(models.Model):

    _name = 'helpdesk.assets.equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'number'
    _description = 'Helpdesk Assests Equipment'

    
    user_id = fields.Many2one(
        'res.users', 
        'Created By', 
        default=lambda self: self.env.uid,
        required=True,
        readonly=True
    )
    
    helpdesk_assets_equipment_line = fields.One2many(
        'helpdesk.assets.equipment.line',
        'helpdesk_assets_equipment_id',
        string='Equipments'
    )

    helpdesk_support_id = fields.Many2one(
        'helpdesk.support', 
        'Support Ticket',
        required=True,
        copy=False,
    )

    state = fields.Selection(
        [('draft','Draft'),
         ('confirm','Confirmed'),
         ('receive','Equipment Received'),
         ('release','Equipment Returned'),
         ('cancel','Cancelled'),],
        default='draft',
        tracking=True,
        copy=False,
    )

    number = fields.Char(
        'Number',
        readonly=True, 
        default=lambda self: _('New')
    )


    reason = fields.Text(
        'Reason',
        required=True
    )

    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.user.partner_id.company_id.id,
        required=True, 
        readonly=True,
        related='helpdesk_support_id.company_id',
    )

    description = fields.Text(
        string="Description",
    )

    color = fields.Integer(
        'Color Index',
        default=0
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )

    team_id = fields.Many2one(
        'support.team',
        string='Helpdesk Team',
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    
    #maintenance_equipment_ids = fields.Many2many(
    #    'maintenance.equipment',
        #string='Equipments'
    #)

    # For state
#    @api.multi odoo13
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'
    
#    @api.multi odoo13
    def action_receive(self):
        for rec in self:
            rec.state = 'receive'
    
    

#    @api.multi odoo13
    def action_release(self):
        for rec in self:
            rec.state = 'release'


#    @api.multi odoo13
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    
#    @api.multi odoo13
    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    # For Sequence
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('helpdesk.assets.equipment')
        return super(helpdeskAssetsEequipment, self).create(vals)

    @api.onchange('helpdesk_support_id')
    def _onchange_project_id(self):
        for rec in self:
            rec.project_id = rec.helpdesk_support_id.project_id.id
            rec.department_id = rec.helpdesk_support_id.department_id.id
            rec.team_id = rec.helpdesk_support_id.team_id.id
            rec.analytic_account_id = rec.helpdesk_support_id.analytic_account_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
