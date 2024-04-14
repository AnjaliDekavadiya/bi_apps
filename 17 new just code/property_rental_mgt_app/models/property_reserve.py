# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

class PropertyBook(models.TransientModel):
    _name = 'property.book'
    _description = "Reserve Rental Property"

    contract_id = fields.Many2one('contract.contract',string="Choose Contract", required=True, help="Default expired and renewal date get by start(from) date for one month contract.")
    property_id = fields.Many2one('product.product', required=True, domain=[('is_property','=',True)])
    desc = fields.Text()
    rent_price = fields.Float()
    owner_id = fields.Many2one('res.partner', string="Property Owner")
    renter_id = fields.Many2one('res.partner', string="Property Renter")
    deposite = fields.Float(string="Monthly Rent", required=True)
    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="Expired Date", required=True, help="Default expired date automatically set for one month after start date. ")
    renewal_date = fields.Date("Renew Date", required=True)
    state = fields.Selection([('avl','Available'),('reserve','Reserve')], string="Status", default='avl')
    contract_month = fields.Integer("Contract Months", help="Rent Contract months calculate base selected contract(monthly/yearly) type.")
    deposite_amount = fields.Float()
    total_deposite  = fields.Float("Total Rent")
    month = fields.Integer()
    discount_offer = fields.Float("Discount Offer (%)")
    offer_price = fields.Float("Offer Price")
    offer_name = fields.Char()

    @api.onchange('from_date','contract_id')
    def check_contract_date(self):
        if self.contract_id:
            if self.contract_id.contract_type == 'monthly':
                self.contract_month = self.contract_id.month
            if self.contract_id.contract_type == 'yearly':
                self.contract_month = self.contract_id.year * 12
            if self.contract_id.contract_type == 'by_date':
                self.from_date = self.contract_id.start_date
                self.to_date = self.contract_id.end_date
                self.contract_month = self.contract_id.month
            self.deposite_amount = self.contract_month * self.deposite
            self.total_deposite = self.deposite_amount
            self.month = self.contract_month
            if self.total_deposite > 0 or self.discount_offer >0:
                discount = self.discount_offer * self.total_deposite/100
                self.offer_price = self.total_deposite - discount

        if self.contract_id and self.from_date:
            if self.contract_id.contract_type == 'monthly':
                self.to_date = self.from_date + relativedelta(months=self.contract_id.month)
            if self.contract_id.contract_type == 'yearly':
                self.to_date = self.from_date + relativedelta(years=self.contract_id.year)
            if self.contract_id.contract_type == 'by_date':
                self.from_date = self.contract_id.start_date
                self.to_date = self.contract_id.end_date

        if self.from_date and self.to_date:
            self.renewal_date = self.to_date
            if self.from_date >= self.to_date:
                raise Warning(_("Select valid contract expired date..!"))
            if self.from_date and self.renewal_date:
                if self.from_date > self.renewal_date:
                    raise Warning(_("Select valid contract renewal date..!"))

    # get rent Property details.
    @api.model
    def default_get(self,default_fields):
        res = super(PropertyBook, self).default_get(default_fields)
        ctx = self._context
        property_data = {
            'deposite_amount':ctx.get('deposite'),
            'property_id':ctx.get('property_id'),
            'desc':ctx.get('desc'),
            'rent_price':ctx.get('rent_price'),
            'renter_id':ctx.get('renter_id'),
            'owner_id':ctx.get('owner_id'),
            'deposite':ctx.get('deposite'),
            'discount_offer':ctx.get('discount_offer'),
            'offer_name':ctx.get('offer_name')
        }
        res.update(property_data)
        return res

    def create_rent_contract(self):
        if self.deposite_amount > 0 and self.discount_offer >0:
            discount = self.discount_offer * self.deposite_amount/100
            self.offer_price = self.deposite_amount - discount
        if self.from_date == fields.Date.today():
            state = 'running'
        else:
            state = 'new'

        # rent offer
        rent_amount = 0
        if self.offer_price and self.month > 0:
            rent_amount = self.offer_price
        else:
            if self.deposite > 0 and self.month > 0:
                rent_amount = self.deposite * self.month
        
        contract_id = self.env['contract.details'].create({
            'contract_month':self.month,
            'deposite':self.deposite_amount,
            'renewal_date':self.renewal_date,
            'rent_price':self.property_id.rent_price,
            'contract_id':self.contract_id.id,
            'owner_id':self.owner_id.id,
            'renewal_date':self.renewal_date,
            'partner_id':self.renter_id.id,
            'property_id':self.property_id.id,
            'date':fields.Date.today(),
            'from_date':self.from_date,
            'to_date':self.to_date,
            'state':state,
            'offer_price':rent_amount,
            'discount_offer':self.discount_offer,
            'offer_name':self.offer_name,
        })
        if contract_id:
            self.property_id.write({'renter_history_ids':[(0,0,{
                'contract_month':self.month,
                'deposite':self.deposite_amount,
                'reference':self.contract_id.name,
                'property_id':self.property_id.id,
                'owner_id':self.owner_id.id, 
                'state':self.state, 
                'rent_price':self.rent_price, 
                'renter_id':self.renter_id.id, 
                'date':fields.Date.today(), 
                'from_date':self.from_date, 
                'to_date':self.to_date, 
                'property_id':self.property_id.id,
                'contract_id': contract_id.id,
                'offer_price':rent_amount,
                'discount_offer':self.discount_offer,
            })]})

            self.property_id.write({'state':'reserve','is_reserved':True,'user_id':self.env.user.id})
            template_id =  self.env.ref('property_rental_mgt_app.property_reserved_template')
            values = template_id._generate_template(self.ids,
                                        ['attachment_ids',
                                         'body_html',
                                         'email_cc',
                                         'email_from',
                                         'email_to',
                                         'mail_server_id',
                                         'model',
                                         'partner_to',
                                         'reply_to',
                                         'res_id',
                                         'scheduled_date',
                                         'subject',
                                        ]
                                    )
            for res_id, val in list(values.items()):
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(val)
                if msg_id:
                    mail_mail_obj.sudo().send(msg_id)

        return {
            'name': 'Contract Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_id':contract_id.id,
            'views': [(self.env.ref('property_rental_mgt_app.property_contract_details_form').id, 'form')],
            'res_model': 'contract.details',
            'domain': [('invoice_id','=',self.property_id.id)],
        }
