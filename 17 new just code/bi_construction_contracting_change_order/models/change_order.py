# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
from odoo.tools import html2plaintext


class ChangeOrder(models.Model):
    _name = 'change.order'
    _description = "change order"
    _rec_name = 'sequence'

    previous = fields.Many2one('change.order', 'previous')
    sequence = fields.Char(string='Number', readonly=True)
    partner_id = fields.Many2one('res.partner', "Customer")
    create_date = fields.Datetime(string="Create Date", default=datetime.now())
    project_id = fields.Many2one('project.project', 'Project')
    analytic_id = fields.Many2one('account.analytic.account', string="Contract/Analytic Account")
    guarantor_one = fields.Many2one('res.partner', string="Guarantor One")
    guarantor_two = fields.Many2one('res.partner', string="Guarantor Two")
    job_order_id = fields.Many2one('job.order', 'Job Order')
    original_completion_date = fields.Date(string="Original Job Completion Date")
    company_id = fields.Many2one('res.company', compute='get_company_id', string="Company")
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    user_id = fields.Many2one('res.users', string='Responsible User', default=lambda self: self.env.uid)
    pricelist = fields.Many2one('product.pricelist', string="Price List")
    estimate_date = fields.Date(string="New Estimation Completion Date")
    confirm_by = fields.Many2one('res.users', string='Confirmed By')
    confirm_date = fields.Date(string="Confirmed Date")
    approve_by = fields.Many2one('res.users', string='Approved By')
    approve_date = fields.Date(string="Approved Date")
    customer_approve = fields.Many2one('res.users', string='Customer Approved')
    customer_approve_date = fields.Date(string="Customer Approved Date")
    closed_by = fields.Many2one('res.users', string='Closed By')
    closed_date = fields.Date(string="Closed Date")
    reason_notes = fields.Text(string="Reason For Change")
    internal_notes = fields.Text(string="Internal Notes")
    term_notes = fields.Text(string="Terms and conditions")
    total_untax_amount = fields.Monetary(store=True, compute='_compute_untax_amount', string="Untaxed Amount",
                                         default=0.0)
    total_taxs_amount = fields.Monetary(store=True, compute='_compute_total_tax_amount', string='Taxes', default=0.0)
    contract_amount = fields.Monetary(string='Original Contract Amount', compute='_compute_contract_amount')
    total_contract_amount = fields.Monetary(compute='_compute_total_contract_amount',
                                            string='Total Contract Amount All Change', default=0.0)
    total_amount = fields.Monetary(store=True, compute='_compute_total_amount', string='Total', default=0.0)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('approve', 'Approved'),
                              ('customer_approve', 'Customer Approved'), ('done', 'Done'), ('close', 'Closed')],
                             'State', default='draft')
    change_order_line_ids = fields.One2many('change.order.line', 'chnage_order_id', 'Change order Lines')
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    sale_order_count = fields.Integer('Sale Order ', compute='_get_sale_order_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('partner_id'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('change_order_seq')
                order_id = self.search([('project_id', '=', int(vals.get('project_id')))], order='id desc', limit=1)
                result = super(ChangeOrder, self).create(vals)
                if order_id != result:
                    result.write({'previous': order_id.id})
                return result
            else:
                vals['sequence'] = self.env['ir.sequence'].next_by_code('change_order_seq')
                return super(ChangeOrder, self).create(vals_list)

    def write(self, vals):
        if vals.get('partner_id') and vals.get('project_id'):
            order_id = self.search([('project_id', '=', int(vals.get('project_id')))], order='id desc', limit=1)
            vals.update({'previous': order_id.id})
            result = super(ChangeOrder, self).write(vals)
            return result
        else:
            return super(ChangeOrder, self).write(vals)

    def check_childs_amount(self):
        for order in self:
            if order.previous:
                self += order.previous.check_childs_amount()

        return self

    def _compute_contract_amount(self):
        self[0].contract_amount = 0.0
        total = 0.0
        order_ids = self[0].check_childs_amount()
        if order_ids:
            order_ids = order_ids - self[0]
            for inv in order_ids:
                if inv.state == 'customer_approve' or inv.state == 'done' or inv.state == 'close':
                    total += inv.total_amount
            self[0].update({'contract_amount': total})

    @api.onchange('project_id')
    def onc_order(self):
        self.analytic_id = self.project_id.analytic_account_id
        if self.job_order_id:
            self.job_order_id.project_id = self.project_id

    @api.onchange('job_order_id')
    def onc_date(self):
        self.original_completion_date = self.job_order_id.end_date
        self.project_id = self.job_order_id.project_id

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = line.pricelist.currency_id

    def get_company_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.company_id = res_user_id.company_id

    def action_confirm(self):
        self.write({'state': 'confirm'})
        for res in self:
            res.write({'confirm_date': datetime.now()})
            res.write({'confirm_by': self.env.uid})

    def action_close(self):
        self.write({'state': 'close'})
        for res in self:
            res.write({'closed_date': datetime.now()})
            res.write({'closed_by': self.env.uid})

    def action_customer_close(self):
        self.write({'state': 'close'})
        for res in self:
            res.write({'closed_date': datetime.now()})
            res.write({'closed_by': self.env.uid})

    def action_done(self):
        self.write({'state': 'done'})

    def action_approve(self):
        self.write({'state': 'approve'})
        for res in self:
            res.write({'approve_date': datetime.now()})
            res.write({'approve_by': self.env.uid})

    def action_customer_approve(self):
        self.write({'state': 'customer_approve'})
        for res in self:
            res.job_order_id.end_date = res.estimate_date
            res.write({'customer_approve_date': datetime.now()})
            res.write({'customer_approve': self.env.uid})

    @api.depends('change_order_line_ids.subtotal')
    def _compute_untax_amount(self):
        total = 0.0
        self.total_untax_amount = 0.0
        for res in self:
            for line in res.change_order_line_ids:
                total += line.subtotal
            res.total_untax_amount = total

    @api.depends('change_order_line_ids.subtotal')
    def _compute_total_tax_amount(self):
        for order in self:
            amount_tax = 0.0
            for line in order.change_order_line_ids:
                amount_tax += line.price_tax
            order.update({
                'total_taxs_amount': amount_tax,
            })

    def _compute_total_contract_amount(self):
        total = 0.0
        self.total_contract_amount = 0.0
        for line in self:
            total = line.total_untax_amount + line.total_taxs_amount + line.contract_amount
            line.total_contract_amount = total

    @api.depends('change_order_line_ids.subtotal')
    def _compute_total_amount(self):
        total = 0.0
        self.total_amount = 0.0
        for line in self:
            total = line.total_untax_amount + line.total_taxs_amount
            line.total_amount = total

    def create_quotation(self):
        tax = []

        for res in self:
            sale_id = self.env['sale.order'].create({
                'partner_id': res.partner_id.id,
                'pricelist_id': res.pricelist.id,
                'origin': res.sequence,
                'change_order_id': self.id,
            })
            for line in res.change_order_line_ids:
                if line.tax_ids:
                    for t in line.tax_ids:
                        tax.append(t.id)
                self.env['sale.order.line'].create({
                    'order_id': sale_id.id,
                    'name': line.description,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.unit_price,
                    'product_uom': line.uom_id.id,
                    'tax_id': [(6, 0, tax)],
                })
            res.sale_id = sale_id.id

    def _get_sale_order_count(self):
        for so in self:
            so_ids = self.env['sale.order'].search([('change_order_id', '=', so.id)])
            so.sale_order_count = len(so_ids)
        return True

    def sale_order_button(self):
        self.ensure_one()
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('change_order_id', '=', self.id)],
        }

    def action_contract(self):
        self.ensure_one()
        return {
            'name': 'Contract',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.account',
            'domain': [('id', '=', self.analytic_id.id)],
        }

    def action_sale_order(self):
        self.ensure_one()
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', '=', self.sale_id.id)],
        }


class ChangeOrderLine(models.Model):
    _name = "change.order.line"
    _description = "change order line"

    chnage_order_id = fields.Many2one('change.order', 'Job Material Planning')
    product_id = fields.Many2one('product.product', 'Product')
    description = fields.Text('Description')
    quantity = fields.Float('Quantity', default=0.0)
    uom_id = fields.Many2one('uom.uom', 'Unit Of Measure')
    unit_price = fields.Float('Sale Price', default=0.0)
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    currency_id = fields.Many2one("res.currency", compute='get_currency_id', string="Currency")
    subtotal = fields.Float(compute='onchange_quantity', string='Sub Total', default=0.0)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)

    @api.depends('quantity', 'unit_price', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            price = line.unit_price
            taxes = line.tax_ids.compute_all(price, line.chnage_order_id.currency_id, line.quantity,
                                             product=line.product_id, partner=line.chnage_order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            })

    @api.constrains('quantity')
    def _check_values(self):
        for line in self:
            if line.quantity <= 0.0:
                raise UserError(_('Values should not be zero or negative.'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if not self.product_id:
            return res
        for rec in self:
            rec.uom_id = rec.product_id.uom_id.id
            rec.description = rec.product_id.name
            rec.unit_price = rec.product_id.lst_price
            rec.quantity = 1.00

    @api.onchange('quantity', 'unit_price')
    def onchange_quantity(self):
        for line in self:
            price = line.quantity * line.unit_price
            line.subtotal = price

    def get_currency_id(self):
        user_id = self.env.uid
        res_user_id = self.env['res.users'].browse(user_id)
        for line in self:
            line.currency_id = line.chnage_order_id.pricelist.currency_id


class SaleOrder(models.Model):
    _inherit = "sale.order"

    change_order_id = fields.Many2one('change.order', string="Change Order")


class ProjectProject(models.Model):
    _inherit = "project.project"

    def action_change_order(self):
        return {
            'name': 'Change Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'change.order',
            'domain': [('project_id', '=', self.id)],
        }


class JobOrder(models.Model):
    _inherit = "job.order"

    def action_change_order(self):
        return {
            'name': 'Change Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'change.order',
            'domain': [('job_order_id', '=', self.id)],
        }


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_change_order(self):
        return {
            'name': 'Change Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'change.order',
            'domain': [('partner_id', '=', self.id)],
        }


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def default_get(self, flds):
        result = super(StockPickingInherit, self).default_get(flds)
        order_id = self.env['change.order'].browse(self._context.get('active_id'))
        result['material_requisition_id'] = order_id.job_order_id.id
        result['job_order_user_id'] = order_id.job_order_id.user_id.id
        result['construction_project_id'] = order_id.project_id.id
        result['analytic_account_id'] = order_id.analytic_id.id
        return result
