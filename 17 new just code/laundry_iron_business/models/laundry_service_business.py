# -*- coding: utf-8 -*-

import time

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LaundryBusinessService(models.Model):
    _name = 'laundry.business.service.custom'
    _description = 'Laundry Business Service'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin', 'portal.mixin']
    
    # @api.model
    # def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('custome_client_user_id', False):
                client_user_id = self.env['res.users'].browse(int(vals.get('custome_client_user_id')))
                if client_user_id:
                    vals.update({'company_id' : client_user_id.company_id.id})
            else:
                vals.update({'custome_client_user_id': self.env.user.id})

            if vals.get('name', False):
                if not vals.get('name', 'New') == 'New':
                    vals['subject'] = vals['name']
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('laundry.business.service.custom') or 'New'
            if vals.get('partner_id', False):
                partner = self.env['res.partner'].sudo().browse(vals['partner_id'])
                if partner:
                    if 'phone' not in vals:
                        vals.update({
                            'phone': partner.phone,
                        })
                    if 'email' not in vals:
                        vals.update({
                            'email': partner.email,
                        })
        return super(LaundryBusinessService, self).create(vals_list)
    
    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_spend_hours(self):
        for rec in self:
            spend_hours = 0.0
            for line in rec.timesheet_line_ids:
                spend_hours += line.unit_amount
            rec.total_spend_hours = spend_hours
    
    @api.onchange('project_id')
    def onchnage_project(self):
        for rec in self:
            rec.analytic_account_id = rec.project_id.analytic_account_id
          
    def set_to_close(self):
        stage_id = self.env['laundry.stage.custom'].search([('stage_type','=','closed')])
        if self.is_close != True:
            self.is_close = True
            self.close_date = fields.Datetime.now()#time.strftime('%Y-%m-%d')
            self.stage_id = stage_id.id
            template = self.env.ref('laundry_iron_business.email_template_laundry_service_custom1')
            template.send_mail(self.id)
            
    def set_to_reopen(self):
        stage_id = self.env['laundry.stage.custom'].search([('stage_type','=','new')])
        if self.is_close != False:
            self.is_close = False
            self.stage_id = stage_id.id

    def create_work_order(self):
        for rec in self:
            work_orde_name = ''
            if rec.subject:
                work_orde_name = rec.subject +'('+rec.name+')'
            else:
                work_orde_name = rec.name
            task_vals = {
                'name' : work_orde_name,
                # 'user_id' : rec.user_id.id,
                #'activity_user_id' : rec.user_id.id,
                'user_ids' : rec.user_id.ids,
                'date_deadline' : rec.close_date,
                'project_id' : rec.project_id.id,
                'partner_id' : rec.partner_id.id,
                'description' : rec.description,
                'laundry_ticket_id' : rec.id,
                'laundry_task_type': 'work_order',
                'nature_of_service_ids': rec.nature_of_service_id.ids,
            }
            task_id= self.env['project.task'].sudo().create(task_vals)
        action = self.env.ref('laundry_iron_business.action_view_task_workorder_laundry')
        result = action.sudo().read()[0]
        result['domain'] = [('id', '=', task_id.id)]
        return result

    def create_sale_order(self):
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        
        for rec in self:
            if not rec.quotation_line_ids:
                raise UserError(_('Please create some quotation lines.'))    
            sale_vals = {
                'partner_id': rec.partner_id.id,
                'date_order': rec.request_date,
                'user_id': rec.user_id.id,
                'analytic_account_id': rec.analytic_account_id.id,
                'company_id': rec.company_id.id
            }
            sale_order_id = sale_obj.sudo().create(sale_vals)
            # sale_order_id.onchange_partner_id() odoo15 27-09-2022
            sale_order_id.laundry_request_id = rec.id
            for line in rec.quotation_line_ids:
                sale_line_vals = {
                    'product_id': line.product_id.id,
                    'name': line.description,
                    'product_uom_qty': line.qty,
                    'product_uom': line.product_uom.id,
                    'price_unit': line.price,
                    'order_id': sale_order_id.id
                }
                sale_line = sale_line_obj.sudo().create(sale_line_vals)
                # sale_line.product_id_change() odoo15 27-09-2022
            # rec.order_id = sale_order_id.id
        action = self.env.ref('sale.action_quotations_with_onboarding')
        result = action.sudo().read()[0]
        result['domain'] = [('id', '=', sale_order_id.id)]
        return result

    def _default_stage_id(self):
        stages = self.env['laundry.stage.custom'].search([],order="sequence, id desc", limit=1).id
        return stages

    name = fields.Char(
        string='Number', 
        required=False,
        default='New',
        copy=False, 
        readonly=True, 
    )
    stage_id = fields.Many2one(
        'laundry.stage.custom',
        string="Stage",
        ondelete='restrict',
        tracking=True, 
        index=True,
        default=_default_stage_id, 
        copy=False
    )
    stage_type = fields.Selection(
        'Type',
        store=True,
        related='stage_id.stage_type',
    )
    email = fields.Char(
        string="Email",
        required=False
    )
    phone = fields.Char(
        string="Phone"
    )
    subject = fields.Char(
        string="Subject"
    )
    description = fields.Text(
        string="Description"
    )
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    request_date = fields.Datetime(
        string='Create Date',
        default=fields.Datetime.now,
        copy=False,
    )
    close_date = fields.Datetime(
        string='Close Date',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )
    timesheet_line_ids = fields.One2many(
        'account.analytic.line',
        'laundry_service_request_id',
        string='Timesheets',
    )
    is_close = fields.Boolean(
        string='Is Request Closed ?',
        tracking=True,
        default=False,
        copy=False,
    )
    total_spend_hours = fields.Float(
        string='Total Hours Spent',
        compute='_compute_total_spend_hours'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    # order_id = fields.Many2one(
    #     'sale.order',
    #     string='Sale Order',
    #     readonly=True,
    #     copy=False,
    # )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    team_id = fields.Many2one(
        'laundry.business.team',
        string='Laundry Team',
        default=lambda self: self.env['laundry.business.team'].sudo()._get_default_team_id(user_id=self.env.uid),
    )
    team_leader_id = fields.Many2one(
        'res.users',
        string='Laundry Manager',
    )
    # journal_id = fields.Many2one(
    #     'account.journal',
    #      string='Journal',
    # )
    # task_id = fields.Many2one(
    #     'project.task',
    #     string='Task',
    #     readonly = True,
    # )
    # is_task_created = fields.Boolean(
    #     string='Is Task Created ?',
    #     default=False,
    # )
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.user.company_id, 
        string='Company',
        readonly=False,
     )
    comment = fields.Text(
        string='Customer Comment',
        readonly=True,
    )
    rating = fields.Selection(
        [('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('very good', 'Very Good'),
        ('excellent', 'Excellent')],
        string='Customer Rating',
        readonly=True,
    )
    product_category = fields.Many2one(
        'product.category',
        string="Product Category"
    )
    product_id = fields.Many2one(
        'product.product',
        domain="[('is_laundry', '=', True)]",
        string="Product"
    )
    problem = fields.Text(
       string="Additional Details",
       copy=True,
    )
    nature_of_service_id = fields.Many2many(
        'laundry.service.type.custom',
        string="Services"
    )
    # lot_id = fields.Many2one(
    #     'stock.production.lot',
    #     string="Lot",
    # )
    total_consumed_hours = fields.Float(
        string='Total Consumed Hours',
    )
    custome_client_user_id = fields.Many2one(
        'res.users',
        string="Request Created User",
        readonly = True,
        track_visibility='always',
    )
    quotation_line_ids = fields.One2many(
        'laundry.line.quot',
        'laundry_id',
        string='Quotation Line'
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Operation Type',
    )
    pickup_type = fields.Selection(
        [('self_pickup','Self Pick Up and Delivery'),
         ('by_us','Pickup and Deilvery By Us')],
        string='Pickup Type',
        copy=False
    )
    address = fields.Text(
        string='Address',
        copy=False,
    )
    expected_pickup_date = fields.Date(
        string='Expected Pickup Date',
        copy=False,
    )
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.email = rec.partner_id.email
                rec.phone = rec.partner_id.phone
    
    @api.onchange('product_category')
    def product_id_change(self):
        return {'domain':{'product_id':[('is_laundry', '=', True),('categ_id', '=', self.product_category.id)]}}

    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            rec.team_leader_id = rec.team_id.leader_id.id
    
    def unlink(self):
        stage_id = self.env['laundry.stage.custom'].search([('name','=','New')],limit=1)
        if stage_id.name != 'New':
            raise UserError(_('You can not delete record which are not in draft state.'))
        return super(LaundryBusinessService, self).unlink()

    def show_work_order_task(self):
        self.ensure_one()
        # for rec in self:
        res = self.env.ref('project.action_view_task')
        res = res.sudo().read()[0]
        res['domain'] = str([('laundry_task_type','=','work_order'), ('laundry_ticket_id', '=', self.id)])
        res['context'] = {'default_laundry_ticket_id': self.id, 'default_laundry_task_type': 'work_order'}
        return res

    def show_sale_order(self):
        # for rec in self:
        self.ensure_one()
        res = self.env.ref('sale.action_quotations_with_onboarding')
        res = res.sudo().read()[0]
        res['domain'] = str([('laundry_request_id', '=', self.id)])
        return res

    def show_custom_picking(self):
        self.ensure_one()
        # for rec in self:
        res = self.env.ref('stock.action_picking_tree_all')
        res = res.sudo().read()[0]
        res['domain'] = str([('laundry_ticket_id', '=', self.id)])
        return res

    @api.model
    def _get_incoming_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)], limit=1)
        return picking_type[:1]

    def _get_destination_location(self):
        self.ensure_one()
        if self.partner_id:
            return self.partner_id.property_stock_customer.id
        return self.picking_type_id.default_location_dest_id.id

    def action_new_incoming_stock_picking(self):
        action = self.env.ref("laundry_iron_business.custom_material_stock_action_picking_new").sudo().read()[0]
        picking_type_id = self._get_incoming_picking_type(self.company_id.id)
        action['context'] = {
            'default_picking_type_id': picking_type_id.id,
            'default_partner_id': self.partner_id.id,
            'default_user_id': False,
            'default_date': self.request_date,
            'default_origin': self.name,
            'default_location_dest_id': self._get_destination_location(),
            'default_location_id': self.partner_id.property_stock_supplier.id,
            'default_company_id': self.company_id.id,
            'default_laundry_ticket_id': self.id,
        }
        return action

class HrTimesheetSheet(models.Model):
    _inherit = 'account.analytic.line'

    laundry_service_request_id = fields.Many2one(
        'laundry.business.service.custom',
        domain=[('is_close','=',False)],
        string='Laundry Business Service',
    )
    billable = fields.Boolean(
        string='Chargable?',
        default=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
