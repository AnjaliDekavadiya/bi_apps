# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerWallet(models.Model):
    _name = "customer.wallet"
    
    name = fields.Char(
        string='Number',
        states={'draft': [('readonly', False)]},
        readonly=True,
        default="New",
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    amount = fields.Float(
        string='Amount',
        required=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now(),
        #required=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    balance_type = fields.Selection(
        selection=[
            ('credit','Credit'),
            ('debit','Debit')],
        string="Balance Type",
        required=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order', 
        string="Sale Order",
        readonly=True,
    )
    reference = fields.Selection([
        ('manual', 'Manual'),
        ('sale_order', 'Sale Order')
        ],
        string='Reference',
        default='manual',
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status',
        default='draft'
    )
    note = fields.Text(
        string="Description"
    )

    #@api.multi
    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('customer.wallet.seq')
        vals.update({
            'name': name
        })
        res = super(CustomerWallet, self).create(vals)
        if res and res.balance_type == 'credit':
            template = self.env.ref('customer_website_wallet.email_template_wallet_balance_credit')
            if template:
                template.sudo().send_mail(res.id)
        if res and res.balance_type == 'debit':
            template = self.env.ref('customer_website_wallet.email_template_wallet_balance_debit')
            if template:
                template.sudo().send_mail(res.id)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
