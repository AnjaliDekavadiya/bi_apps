# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import fields, models,api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime

class courier_request(models.Model):
    _name = 'dev.courier.request'
    _description = 'Courier Request'
    _inherit = ['mail.thread.cc','portal.mixin','mail.activity.mixin']
    _order = "id desc"
    _fold_name = 'fold'
    
    @api.model
    def get_default_state(self):
        return self.env['dev.courier.stages'].search([], order='sequence', limit=1).id

    @api.onchange('signature')
    def onchange_signature(self):
        self.signature_date = datetime.now()

    name = fields.Char('Name', default='/', copy=False)
    sender_id = fields.Many2one('res.partner', string='Sender', required="1", domain=[('courier', '=', True)])
    sender_name = fields.Char('Sender Name', required="1", tracking=True)
    sender_street = fields.Char('Sender Street', required="1")
    sender_street2 = fields.Char('Sender Street2')
    sender_city = fields.Char('Sender City', required="1")
    sender_state_id = fields.Many2one('res.country.state', string='Sender State', required="1")
    sender_country_id = fields.Many2one('res.country', string='Sender Country', required="1")
    sender_zip = fields.Char('Sender Zip', required="1")
    sender_mobile = fields.Char('Sender Mobile', required="1", tracking=True)
    sender_email = fields.Char('Sender Email', required="1")
    
    receiver_id = fields.Many2one('res.partner', string='Receiver', required="1", domain=[('courier', '=', True)])
    receiver_name = fields.Char('Sender Name', required="1", tracking=True)
    receiver_street = fields.Char('Street', required="1")
    receiver_street2 = fields.Char('Street2')
    receiver_city = fields.Char('City', required="1")
    receiver_state_id = fields.Many2one('res.country.state', string='State', required="1")
    receiver_country_id = fields.Many2one('res.country', string='Country', required="1")
    receiver_zip = fields.Char('Zip', required="1")
    receiver_mobile = fields.Char('Receiver Mobile', required="1", tracking=True)
    receiver_email = fields.Char('Receiver Email', required="1")
    
    
    registration_date = fields.Date('Registration Date', default=datetime.today(), required="1", tracking=True)
    delivery_date = fields.Date('Delivery Date', required="1", tracking=True)
    courier_type_id = fields.Many2one('dev.courier.type', string='Type', required="1", tracking=True)
    category_id = fields.Many2one('dev.courier.category', string='Category', required="1", tracking=True)
    priority_id = fields.Many2one('dev.courier.priority', string='Priority', required="1", tracking=True)
    
    
    tag_ids = fields.Many2many('dev.courier.tags', string='Tags')
    total_km = fields.Integer('Kilometres', required="1", tracking=True)
    user_id = fields.Many2one('res.users', default=lambda self:self.env.user, required="1")
    company_id = fields.Many2one('res.company', default=lambda self:self.env.company, required="1")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Currency')
    state_id = fields.Many2one('dev.courier.stages', string='Status',compute='_compte_stage_id', index=True, tracking=True,
                                readonly=False, store=True, group_expand='_read_group_stage_ids', ondelete='restrict',
                                default=get_default_state)
    
    courier_lines = fields.One2many('courier.request.lines', 'request_id', string='Courier Lines')
    notes = fields.Text('Notes')
    courier_charge = fields.Monetary('Courier Charge', compute='_get_courier_charge')
    distance_charge = fields.Monetary('Distance Charge', compute='_get_distance_charge')
    edi_distance_charge = fields.Monetary('Distance Charges')
    edi_additional_charge = fields.Monetary('Additional Charges')
    additional_charge = fields.Monetary('Additional Charge', compute='_get_additional_charge')
    total_charge_amount = fields.Monetary('Total Charge', compute='_get_total_charge', store=True)
    invoice_count = fields.Integer('Invoice Count', compute='_get_invoice_count')
    allow_invoice = fields.Boolean('Allow Invoice', compute='compute_allow_invoice')
    color = fields.Integer()
    fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    courier_image_ids = fields.One2many('ir.attachment', 'courier_request_id', string='Parcel Images')
    total_parcel = fields.Integer(string='Total Parcel', compute='_compute_total_parcel')
    signature_name = fields.Char(string='Full Name', tracking=True, copy=False)
    signature_date = fields.Datetime(string='Signature Date', tracking=True, copy=False)
    signature = fields.Binary(string='Signature', copy=False)

    @api.depends('courier_lines')
    def _compute_total_parcel(self):
        for rec in self:
            parcel = sum(line.quantity for line in self.courier_lines)
            rec.total_parcel = parcel

    def get_formatted_date(self):
        date = datetime.strptime(str(self.registration_date), "%Y-%m-%d").strftime('%d/%m/%Y')
        return date

    def send_by_mail(self):
        self.ensure_one()
        template_id = self.env.ref('dev_courier_management.template_dev_courier_request_send_by_mail')
        ctx = {
            'default_model': 'dev.courier.request',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id and template_id.id ),
            'default_template_id': template_id and template_id.id or False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': False,
            'view_id': False ,
            'target': 'new',
            'context': ctx,
        }
        
    def _get_invoice_count(self):
        for rec in self:
            invoice_ids = self.env['account.move'].sudo().search([('courier_request_id','=',rec.id),
                                                                  ('move_type','=','out_invoice')])
            rec.invoice_count = len(invoice_ids)
    
    @api.onchange('sender_id')
    def onchange_sender(self):
        if self.sender_id:
            vals={
                'sender_name':self.sender_id.name or '',
                'sender_street':self.sender_id.street or '',
                'sender_street2':self.sender_id.street2 or '',
                'sender_city':self.sender_id.city or '',
                'sender_state_id':self.sender_id.state_id.id or False,
                'sender_country_id':self.sender_id.country_id.id or False,
                'sender_zip':self.sender_id.zip or False,
                'sender_mobile':self.sender_id.mobile or self.sender_id.phone or False,
                'sender_email':self.sender_id.email or ''
            }
            self.write(vals)
        else:
            vals={
                'sender_name':'',
                'sender_street':'',
                'sender_street2':'',
                'sender_city':False,
                'sender_state_id':False,
                'sender_country_id':False,
                'sender_city':False,
                'sender_zip':'',
                'sender_mobile':'',
                'sender_email':''
            }
            self.write(vals)
    
    
    @api.onchange('receiver_id')
    def onchange_receiver(self):
        if self.receiver_id:
            vals={
                'receiver_name':self.receiver_id.name or '',
                'receiver_street':self.receiver_id.street or '',
                'receiver_street2':self.receiver_id.street2 or '',
                'receiver_city':self.receiver_id.city or '',
                'receiver_state_id':self.receiver_id.state_id.id or False,
                'receiver_country_id':self.receiver_id.country_id.id or False,
                'receiver_zip':self.receiver_id.zip or False,
                'receiver_mobile':self.receiver_id.mobile or self.receiver_id.phone or False,
                'receiver_email':self.receiver_id.email or '',
            }
            self.write(vals)
        else:
            vals={
                'receiver_name':'',
                'receiver_street':'',
                'receiver_street2':'',
                'receiver_city':False, 'receiver_state_id':False,
                'receiver_country_id':False, 'receiver_city':False,
                'receiver_zip':'',
                'receiver_mobile':'',
                'receiver_email':'',
            }
            self.write(vals)
            
    @api.depends('total_km','edi_distance_charge')
    def _get_distance_charge(self):
        for request in self:
            if request.edi_distance_charge:
                request.distance_charge = request.edi_distance_charge
            else:
                dis_id = self.env['dev.courier.distance.rule'].search([('from_km','<=',request.total_km),
                                                                       ('to_km','>=',request.total_km)], order='id', limit=1)
                if dis_id:
                    request.distance_charge = dis_id.price
                    request.edi_distance_charge = dis_id.price
                else:
                    request.distance_charge = 0
                    request.edi_distance_charge = 0
    
    @api.depends('courier_charge','priority_id','total_km','edi_additional_charge')
    def _get_additional_charge(self):
        for request in self:
            if request.edi_additional_charge:
                request.additional_charge = request.edi_additional_charge
            else:
                amount = ((request.courier_charge * request.total_km)/100) * request.priority_id.price
                request.additional_charge = amount
                request.edi_additional_charge = amount
            
            
    @api.depends('courier_lines','courier_lines.total_price')
    def _get_courier_charge(self):
        for request in self:
            request.courier_charge = sum([line.total_price for line in request.courier_lines])
            
    @api.depends('courier_charge','distance_charge','additional_charge')
    def _get_total_charge(self):
        for request in self:
            request.total_charge_amount = request.courier_charge + request.distance_charge + request.additional_charge
            
    @api.depends('sender_name')
    def _compte_stage_id(self):
        for request in self:
            if not request.state_id:
                request.state_id = self.env['dev.courier.stages'].search([], order='sequence', limit=1).id
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain=[]
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('dev.courier.sequence') or 'New'
        request_id = super(courier_request, self).create(vals)
        if request_id.sender_id:
            if request_id.sender_id.id not in request_id.message_partner_ids.ids:
                request_id.message_subscribe(partner_ids=request_id.sender_id.ids)
        if request_id.receiver_id:
            if request_id.receiver_id.id not in request_id.message_partner_ids.ids:
                request_id.message_subscribe(partner_ids=request_id.receiver_id.ids)
        return request_id
    
    @api.onchange('sender_state_id','receiver_state_id')
    def onchange_state(self):
        if self.sender_state_id:
            self.sender_country_id = self.sender_state_id.country_id and self.sender_state_id.country_id.id or False
        if self.receiver_state_id:
            self.receiver_country_id = self.receiver_state_id.country_id and self.receiver_state_id.country_id.id or False
    
    
    def unlink(self):
        for request in self:
            name = ''
            for state in request.company_id.cur_delete_state_ids:
                if name:
                    name = name + ', '+ state.name
                else:
                    name = state.name
                    
            if request.state_id.id not in request.company_id.cur_delete_state_ids.ids:
                raise ValidationError(_("Request can be deleted only in '%s' states !")% (name))
        return super(courier_request,self).unlink()    
    
    
    def get_courier_product_lines(self):
        inv_line = []
        for line in self.courier_lines:
            tax_ids = []
            product_id = self.company_id.courier_product_id
            if product_id.taxes_id:
                tax_ids = product_id.taxes_id.ids
            price = line.price
            if line.dim_price > price:
                price = line.dim_price
            inv_line.append((0,0,{
                'product_id':product_id.id,
                'quantity':line.quantity,
                'name':line.name,
                'product_uom_id':product_id.uom_id and product_id.uom_id.id or False ,
                'price_unit':price,
                'tax_ids':[(6,0, tax_ids)],
                }))
        if self.company_id.distance_product_id and self.distance_charge:
            product_id = self.company_id.distance_product_id
            tax_ids=[]
            if product_id.taxes_id:
                tax_ids = product_id.taxes_id.ids
            price = self.distance_charge
            inv_line.append((0,0,{
                'product_id':product_id.id,
                'quantity':1,
                'name':'Distance Charge',
                'product_uom_id':product_id.uom_id and product_id.uom_id.id or False ,
                'price_unit':price,
                'tax_ids':[(6,0, tax_ids)],
                }))
        
        if self.company_id.additional_charge_pro_id and self.additional_charge:
            product_id = self.company_id.additional_charge_pro_id
            tax_ids=[]
            if product_id.taxes_id:
                tax_ids = product_id.taxes_id.ids
            price = self.additional_charge
            inv_line.append((0,0,{
                'product_id':product_id.id,
                'quantity':1,
                'name':'Additional Charge',
                'product_uom_id':product_id.uom_id and product_id.uom_id.id or False ,
                'price_unit':price,
                'tax_ids':[(6,0, tax_ids)],
                }))
        return inv_line
        
    @api.depends('state_id')
    def compute_allow_invoice(self):
        for request in self:
            if request.state_id.allow_create_invoice:
                request.allow_invoice = True
            else:
                request.allow_invoice = False
    
    def action_view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        invoice_ids = self.env['account.move'].search([('courier_request_id','=',self.id),
                                                       ('move_type','=','out_invoice')])
        if len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids.ids)]
        elif invoice_ids:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoice_ids.id
        action['context']={
            'create':0,
            }
        return action
        
    def create_customer_invoice(self):
        journal_pool = self.env['account.journal'].sudo()
        journal_id = journal_pool.search([('type','=','sale')],limit=1)
        if not journal_id:
            raise ValidationError(_('Please Create Sale Journal'))
        if not self.company_id.courier_product_id:
            raise ValidationError(_('Please Select Courier Product in Courier Setting.'))
        if not self.company_id.distance_product_id:
            raise ValidationError(_('Please Select Distance Charge Product in Courier Setting.'))
        if not self.company_id.additional_charge_pro_id:
            raise ValidationError(_('Please Select Additional Charge Product in Courier Setting.'))
        inv_val = {
            'partner_id':self.sender_id and self.sender_id.id or False,
            'courier_request_id':self.id,
            'move_type':'out_invoice',
            'journal_id':journal_id and journal_id.id or False,
            'currency_id':self.currency_id and self.currency_id.id or False,
            'invoice_line_ids':self.get_courier_product_lines(),
            'state':'draft',
            'company_id':self.company_id and self.company_id.id or False,
        }
        inv_id = self.env['account.move'].create(inv_val)
        if inv_id:
            action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = inv_id.id
            context = {
                'default_move_type': 'out_invoice',
                "create":False,
            }
            return action
       
class courier_lines(models.Model):
    _name = "courier.request.lines"
    _description = 'Courier Details'
    
    name = fields.Char('Name', required="1")
    description = fields.Char(string='Description')
    quantity = fields.Integer('Quantity', default=1, required="1")
    weight = fields.Float('Weight(KG)', required="1")
    dimension_id = fields.Many2one('dev.courier.dimension.rule', string='L X W X H')
    price = fields.Monetary('Weight Price')
    dim_price = fields.Monetary('Dimension Price')
    total_price = fields.Monetary('Subtotal', compute='_get_total_price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    request_id = fields.Many2one('dev.courier.request', string='Courier Request')
    
    @api.depends('quantity','price','dim_price')
    def _get_total_price(self):
        for line in self:
            price = line.price 
            if line.dim_price > line.price:
                price = line.dim_price
            line.total_price = line.quantity * price
            
    @api.onchange('weight')
    def onchange_weight(self):
        if self.weight:
            rule_id = self.env['dev.courier.weight.rule'].search([('from_weight','<=',self.weight),
                                                                  ('to_weight','>=',self.weight)], order="id", limit=1)
            if rule_id:
                self.price = rule_id.price
            else:
                self.price = 0
        else:
            self.price = 0
                        
    @api.onchange('dimension_id')
    def onchange_dimension(self):
        if self.dimension_id:
            self.dim_price = self.dimension_id.price
        else:
            self.dim_price = 0.0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
