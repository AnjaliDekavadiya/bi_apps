# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RepairOrderInspection(models.Model):
    _name = "repair.order.inspection"
    _description = 'Repair Order Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order= 'id desc'

    name = fields.Char(
        string="Number",
        readonly=True,
    )
    task_id = fields.Many2one(
        'project.task',
        string="Work Order",
        required=True,
    )
    create_date = fields.Date(
        string="Create Date",
    )
    company_id = fields.Many2one(
        'res.company',
        string = "Company",
        related = 'user_id.company_id',
        readonly = True,
        default=lambda self: self.env.user.company_id,
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        default=lambda self: self.env.user,
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('process', 'Processed'),
        ('complet', 'Completed'),
        ('cancel', 'Cancelled')],
        default='draft',
        tracking=True,
        copy=False,
    )
    inspector_id = fields.Many2one(
        'res.partner',
        string="Inspection Responsible",
    )
    inspection_line = fields.One2many(
        'repair.order.inspection.line',
        'repair_inspection_id',
        string="Inspection Line",
    )
    machine_repair_id = fields.Many2one(
        'machine.repair.support',
        string="Machine Repair",
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account",
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        required=True,
    )
    subject = fields.Char(
        string="Subject",
        required=True,
    )
    internal_note = fields.Text(
        string="Internal Note",
    )
    inspection_result = fields.Many2one(
        'repair.inspection.result',
        string='Inspection Result',
    )
    image1 = fields.Binary(
        string="Photo 1",
    )
    image2 = fields.Binary(
        string="Photo 2",
    )
    image3 = fields.Binary(
        string="Photo 3",
    )
    image4 = fields.Binary(
        string="Photo 4",
    )
    image5 = fields.Binary(
        string="Photo 5",
    )
    result_description = fields.Text(
        string="Result Description",
    )
    inspection_location = fields.Char(
        string="Inspection Location",
    )
    reference = fields.Char(
        string="Reference Specification",
    )
    inspection_start = fields.Datetime(
        string="Inspection Start Date",
    )
    inspection_end = fields.Datetime(
        string="Inspection End Date",
    )
    confirm_by_id = fields.Many2one(
        'res.users', 
        string='Confirmed By',
        readonly=True,
        copy=False,
    )
    process_by_id = fields.Many2one(
        'res.users', 
        string='Processed By',
        readonly=True,
        copy=False,
    )
    done_by_id = fields.Many2one(
        'res.users', 
        string='Completed By',
        readonly=True,
        copy=False,
    )
    cancel_by_id = fields.Many2one(
        'res.users', 
        string='Cancelled By',
        readonly=True,
        copy=False,
    )
    confirm_date = fields.Date(
        string='Confirmed Date',
        readonly=True,
        copy=False,
    )
    process_date = fields.Date(
        string='Processed Date',
        readonly=True,
        copy=False,
    )
    done_date = fields.Date(
        string='Completed Date',
        readonly=True,
        copy=False,
    )
    cancel_date = fields.Date(
        string='Cancelled Date',
        readonly=True,
        copy=False,
    )
    inspection_type_id = fields.Many2one(
        'repair.inspection.type',
        string="Inspection Type",
    )
    subcontractor_id = fields.Many2one(
        'res.partner',
        string="Subcontractor",
    )
    country_id = fields.Many2one(
        'res.country',
        string="Country",
    )
    reference_drawing = fields.Binary(
        string="Reference Drawing",
    )

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('repair.inspection.seq')
        vals.update({
            'name': name
            })
        return super(RepairOrderInspection, self).create(vals)

    # @api.multi
    def set_to_confirm(self):
        for rec in self:
            rec.confirm_by_id = self.env.user.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'confirm'

    # @api.multi
    def set_to_done(self):
        for rec in self:
            rec.done_by_id = self.env.user.id
            rec.done_date = fields.Date.today()
            rec.state = 'complet'

    # @api.multi
    def set_to_cancel(self):
        for rec in self:
            rec.cancel_by_id = self.env.user.id
            rec.cancel_date = fields.Date.today()
            rec.state = 'cancel'

    # @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for rec in self:
            rec.analytic_account_id = rec.project_id.analytic_account_id.id

    # @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You can not delete this record."))
        return super(RepairOrderInspection, self).unlink()

    # @api.multi
    def set_to_processed(self):
        for rec in self:
            rec.process_by_id = self.env.user.id
            rec.process_date = fields.Date.today()
            rec.state = 'process'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
