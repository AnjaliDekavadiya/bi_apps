# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ClothRequestDetails(models.Model):
    _name = 'cloth.request.details'
    _description = 'Cloth Request Details'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    def _default_stage_id(self):
        stage_id = self.env['cloth.request.stage'].search([], order='sequence', limit=1).id
        return stage_id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages = self.env['cloth.request.stage'].search(domain, order=order)
        search_domain = [('id', 'in', stages.ids)]
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    name = fields.Char(
        string='Cloth Request Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        index=True, 
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True
    )
    request_date = fields.Date(
        string="Request Date",
        default=fields.Date.context_today,
        required=True
    )
    deadline_date = fields.Date(
        string="Deadline Date",
    )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')],
        string="Gender",
        default='male'
    )
    cloth_type_id = fields.Many2one(
        'cloth.measurement.details',
        domain="[('partner_id', '=', partner_id)]",
        string="Customer Measurement",
    )
    measurement_ids = fields.One2many(
        'cloth.measurement.details.line',
        'cloth_request_id',
        string="Measurement Types"
    )
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
        index=True, 
        default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible",
        default=lambda self: self.env.user
    )
    internal_note = fields.Text(
        'Add an internal note...',
    )
    special_note = fields.Text(
        'Add an special note...',
    )
    stage_id = fields.Many2one(
        'cloth.request.stage', 
        string='Stage', 
        tracking=True, 
        index=True, 
        copy=False,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id()
    )
    quantity = fields.Float(
        string="Quantity"
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure"
    )
    lead_id = fields.Many2one(
        'crm.lead',
        readonly=True,
        string="Lead"
    )
    fabric_remarks = fields.Char(
        string="Fabric"
    )
    fabric_color = fields.Char(
        string="Fabric Color"
    )

    @api.onchange('partner_id','cloth_type_id')
    def _onchange_partner_id(self):
        for rec in self:
            return {'domain': {'cloth_measurement_ids': [
                ('partner_id', '=', rec.partner_id.id),
                ('cloth_type_id', '=', rec.cloth_type_id.id)
            ]}}

    def action_sale_quotations_new(self):
        if not self.partner_id:
            # return self.env.ref("cloth_tailor_management_odoo.cloth_request_quotation_partner_action").sudo().read()[0]
            return self.env['ir.actions.actions']._for_xml_id('cloth_tailor_management_odoo.cloth_request_quotation_partner_action')
        else:
            return self.action_new_quotation()

    def action_new_quotation(self):
        # action = self.env.ref("cloth_tailor_management_odoo.custom_sale_action_quotations_new").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_management_odoo.custom_sale_action_quotations_new')
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_origin': self.name,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_custom_cloth_request_ids': [(6, 0, self.ids)]
        }
        return action

    def action_view_invoice(self):
        invoices = self.env['account.move'].sudo().search([('custom_cloth_request_ids', 'in', self.id)])
        # action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def action_view_sale_order(self):
        orders = self.env['sale.order'].sudo().search([('custom_cloth_request_ids', 'in', self.id)])
        # action = self.env.ref('sale.action_quotations_with_onboarding').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('sale.action_quotations_with_onboarding')
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        if len(self) == 1:
            context = {
                'default_partner_id': self.partner_id.id,
                'default_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            }
        action['context'] = context
        return action

    def action_view_measurement(self):
        measurements = self.cloth_type_id
        # action = self.env.ref('cloth_tailor_management_odoo.action_cloth_measurement_details').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_management_odoo.action_cloth_measurement_details')
        if len(measurements) > 1:
            action['domain'] = [('id', 'in', measurements.ids)]
        elif len(measurements) == 1:
            form_view = [(self.env.ref('cloth_tailor_management_odoo.cloth_measurement_details_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = measurements.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        action['context'] = {}
        return action

    def action_view_tasks(self):
        tasks = self.env['project.task'].sudo().search([('cloth_request_id', '=', self.id)])
        # action = self.env.ref('project.action_view_task').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('project.action_view_task')
        if len(tasks) > 1:
            action['domain'] = [('id', 'in', tasks.ids)]
        elif len(tasks) == 1:
            form_view = [(self.env.ref('project.view_task_form2').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = tasks.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        action['context'] = {}
        return action


    def action_get_measurment_line(self):
        for rec in self:
            if rec.cloth_type_id and not rec.measurement_ids:
                for line in rec.cloth_type_id.measurement_ids:
                    new_line_id = self.env['cloth.measurement.details.line'].create({
                        'cloth_request_id': rec.id,
                        'measurement_details_line_id': line.id,
                        'measurement': line.measurement,
                        'uom_id': line.uom_id.id,
                        'cloth_measurement_type_id': line.cloth_measurement_type_id.id
                    })


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cloth.request.details') or _('New')
        return super(ClothRequestDetails, self).create(vals)
