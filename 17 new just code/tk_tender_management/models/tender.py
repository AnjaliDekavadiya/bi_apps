# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models
from odoo.exceptions import UserError, ValidationError


class TenderInformation(models.Model):
    _name = 'tender.information'
    _description = "Tender Information"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Title", tracking=True, translate=True)
    start_date = fields.Date(string="Tender Start Date")
    end_date = fields.Date(string="Tender End Date")
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user and self.env.user.id or False,
                                     string="Responsible")
    desc = fields.Html(string="Description")
    stage = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('bid_submission', 'Bid Submission'),
                              ('bid_evaluation', 'Bid Evaluation'),
                              ('bid_selection', 'Bid Selection'),
                              ('close', 'Close'),
                              ('cancel', 'Cancel')],
                             tracking=True,
                             default='draft')
    tender_type_id = fields.Many2one('tender.type', string="Category")
    is_site_specific = fields.Boolean(related="tender_type_id.is_site_specific", store=True)
    bid_start_date = fields.Date(string="Bid Start Date")
    bid_end_date = fields.Date(string="Bid End Date")
    bid_id = fields.Many2one('tender.bidding', string="Bid")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    state = fields.Selection(related="purchase_order_id.state", string="Status")
    cancellation_reason = fields.Html(string="Cancellation Reason")
    type = fields.Selection([('single_vendor', 'Single Vendor for all Product'),
                             ('multiple_vendor', 'Product wise vendor')], required=True)
    confirm_bid = fields.Boolean()

    # Address
    zip = fields.Char(string='Pin Code', translate=True)
    street = fields.Char(string='Street1', translate=True)
    street2 = fields.Char(string='Street2', translate=True)
    city = fields.Char(string='City', translate=True)
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one(
        "res.country.state", string='State', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")

    # One2many
    tender_order_line = fields.One2many('tender.info.line', 'tender_id', string='Tender Order Line')
    tender_document_ids = fields.One2many('tender.document.line', 'tender_id', string="Tender Document", tracking=True)
    tender_bid_ids = fields.One2many('tender.bidding', 'tender_id', string="Tender Bidding", tracking=True)

    # Count & Total
    bid_count = fields.Integer(string="Bid Count", compute="_compute_count")
    qualified_bid_count = fields.Integer(string="Qualified Bid Count", compute="_compute_count")
    legit_bid_count = fields.Integer(string="Legit Bid Count", compute="_compute_count")
    bill_count = fields.Integer(string="Bill Count", compute="_compute_count")
    delivery_count = fields.Integer(string="Delivery Count", compute="_compute_count")
    multiple_bid_count = fields.Integer(string="Multiple Bid Count", compute="_compute_count")
    purchase_count = fields.Integer(string="Purchase Count", compute="_compute_count")

    # constrain Create Write
    @api.constrains('start_date', 'end_date', 'bid_start_date')
    def _check_bid_start_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if not record.start_date <= record.bid_start_date <= record.end_date:
                    raise ValidationError("Invalid bid start date. Must be within tender start and end dates.")

    @api.constrains('bid_start_date', 'end_date', 'bid_end_date')
    def _check_bid_start_date(self):
        for record in self:
            if record.bid_start_date and record.end_date:
                if not record.end_date >= record.bid_end_date > record.bid_start_date:
                    raise ValidationError(
                        "Invalid bid end date. Must be within bid start date and tender end date.")

    @api.constrains('tender_order_line')
    def _check_product_id(self):
        for record in self.tender_order_line:
            if not record.display_type:
                duplicates = self.tender_order_line.filtered(
                    lambda r: r.id != record.id and r.product_id.id == record.product_id.id)
                if duplicates:
                    raise ValidationError("Product Already Added !")

    # Compute
    @api.depends('type')
    def _compute_count(self):
        for rec in self:
            delivery_count = 0
            rec.bid_count = self.env['tender.bidding'].search_count([('tender_id', '=', rec.id)])
            rec.qualified_bid_count = self.env['tender.bidding'].search_count(
                [('tender_id', '=', rec.id), ('qualify_status', '=', 'qualified')])
            rec.legit_bid_count = self.env['tender.bidding'].search_count([('tender_id', '=', rec.id),
                                                                           ('is_legit_bid', '=', True)])
            rec.bill_count = self.env['account.move'].search_count([('tender_id', '=', rec.id)])
            rec.delivery_count = self.env['stock.picking'].search_count(
                [('purchase_id', '=', rec.purchase_order_id.id)])
            rec.multiple_bid_count = self.env['tender.bidding'].search_count(
                [('tender_id', '=', rec.id), ('qualify_status', '=', 'qualified')])
            rec.purchase_count = self.env['purchase.order'].search_count([('tender_id', '=', rec.id)])
            if rec.type == "single_vendor":
                delivery_count = self.env['stock.picking'].search_count(
                    [('purchase_id', '=', rec.purchase_order_id.id)])
            elif rec.type == "multiple_vendor":
                purchase_ids = self.env['purchase.order'].search([('tender_id', '=', rec.id)]).mapped('id')
                delivery_count = self.env['stock.picking'].search_count([('purchase_id', 'in', purchase_ids)])
            rec.delivery_count = delivery_count

    # Buttons
    def action_stage_draft(self):
        self.stage = "draft"

    def action_confirm_tender(self):
        self.stage = "confirm"

    def action_tender_cancel(self):
        self.stage = "cancel"

    def action_bid_submission(self):
        self.stage = 'bid_submission'

    def action_bid_evaluation(self):
        if self.type == "single_vendor":
            self.stage = 'bid_evaluation'
        else:
            self.stage = "bid_selection"
        for data in self.tender_bid_ids:
            if data.stage == "bid":
                data.stage = "bid_close"

    def action_confirm_bid_selection(self):
        self.stage = "bid_selection"
        for rec in self.tender_bid_ids:
            if rec.id == self.bid_id.id:
                rec.stage = "won"
                mail_template = self.env.ref('tk_tender_management.bid_selection_mail_template')
                if mail_template:
                    mail_template.send_mail(rec.id, force_send=True)
            else:
                rec.stage = "lost"
                if rec.qualify_status == "qualified":
                    mail_template = self.env.ref('tk_tender_management.bid_selection_lost_mail_template')
                    if mail_template:
                        mail_template.send_mail(rec.id, force_send=True)

    def action_confirm_multiple_vendor_po(self):
        self.confirm_bid = True

    def action_create_po(self):
        msg = ""
        vendor_ids = []
        if self.type == "single_vendor":
            if self.bid_id:
                lines = []
                for product in self.bid_id.bidding_line_ids:
                    record = {
                        'display_type': product.display_type,
                        'sequence': product.sequence,
                        'product_id': product.product_id.id,
                        'name': product.name,
                        'product_qty': product.qty if not product.display_type else 0,
                        'product_uom': product.uom_id.id,
                        'price_unit': product.price
                    }
                    lines.append((0, 0, record))
                purchase_record = {
                    'partner_id': self.bid_id.vendor_id.id,
                    'order_line': lines,
                    'tender_id': self.id,
                }
                purchase_order_id = self.env['purchase.order'].create(purchase_record)
                self.purchase_order_id = purchase_order_id.id
                self.stage = "close"
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Purchase Order',
                    'res_model': 'purchase.order',
                    'res_id': purchase_order_id.id,
                    'view_mode': 'form',
                    'target': 'current'
                }
        elif self.type == "multiple_vendor":
            product_ids = self.env['tender.info.line'].search(
                [('display_type', '=', False), ('tender_id', '=', self.id)]).mapped('product_id').mapped('id')
            bidding_product_ids = self.env['tender.bidding.line'].search(
                [('tender_id', '=', self.id), ('selected_bid', '=', True), ('display_type', '=', False)]).mapped(
                'product_id').mapped('id')
            if set(product_ids) == set(bidding_product_ids):
                for data in self.tender_bid_ids:
                    if data.qualify_status == "qualified":
                        for line in data.bidding_line_ids:
                            if line.selected_bid and not line.display_type:
                                vendor_ids.append(line.vendor_id.id)
                sorted_vendor_ids = list(set(vendor_ids))
                for vendor in sorted_vendor_ids:
                    for data in self.tender_bid_ids:
                        if data.qualify_status == "qualified":
                            order_lines = []
                            for line in data.bidding_line_ids:
                                if line.selected_bid and not line.display_type and line.vendor_id.id == vendor:
                                    purchase_line = {
                                        'product_id': line.product_id.id,
                                        'name': line.name,
                                        'product_qty': line.qty,
                                        'product_uom': line.uom_id.id,
                                        'price_unit': line.price
                                    }
                                    order_lines.append((0, 0, purchase_line))
                            if len(order_lines) > 0:
                                purchase_rec = {
                                    'partner_id': vendor,
                                    'order_line': order_lines,
                                    'tender_id': self.id,
                                }
                                self.env['purchase.order'].create(purchase_rec)
                selected_bid = self.env['tender.bidding.line'].search(
                    [('tender_id', '=', self.id), ('selected_bid', '=', True)]).mapped(
                    'tender_bidding_id')
                rejected_bid = self.env['tender.bidding.line'].search(
                    [('tender_id', '=', self.id), ('selected_bid', '=', False)]).mapped(
                    'tender_bidding_id')
                for data in selected_bid:
                    data.stage = "won"
                    mail_template = self.env.ref('tk_tender_management.multiple_vendor_bid_selection_mail_template')
                    if mail_template:
                        mail_template.send_mail(data.id, force_send=True)
                for rec in rejected_bid:
                    if not rec.stage == "won":
                        rec.stage = "lost"
                        mail_template = self.env.ref('tk_tender_management.bid_selection_lost_mail_template')
                        if mail_template:
                            mail_template.send_mail(rec.id, force_send=True)
                self.stage = "close"

            else:
                missing_product_ids = list(set(product_ids).difference(bidding_product_ids))
                missing_product = self.env['product.product'].browse(missing_product_ids)
                for data in missing_product:
                    msg = msg + "[" + str(data.default_code) + "] " + data.name + "\n"
                raise ValidationError(
                    "Following Products available in tender, but not selected in bid. Please choose and retry." + "\n" + msg)

    # Smart Button
    def action_view_all_bid(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'All Bids',
            'res_model': 'tender.bidding',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_qualified_bid(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Qualified Bids',
            'res_model': 'tender.bidding',
            'domain': [('tender_id', '=', self.id), ('qualify_status', '=', 'qualified')],
            'context': {'default_tender_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_legit_bid(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Legit Bids',
            'res_model': 'tender.bidding',
            'domain': [('tender_id', '=', self.id), ('is_legit_bid', '=', True)],
            'context': {'default_tender_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_delivery_order(self):
        if self.type == "single_vendor":
            ids = [self.purchase_order_id.id]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Delivery Orders',
                'res_model': 'stock.picking',
                'domain': [('purchase_id', 'in', ids)],
                'context': {'create': False},
                'view_mode': 'tree,form,kanban',
                'target': 'current'
            }
        elif self.type == "multiple_vendor":
            ids = self.env['purchase.order'].search([('tender_id', '=', self.id)]).mapped('id')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Delivery Orders',
                'res_model': 'stock.picking',
                'domain': [('purchase_id', 'in', ids)],
                'context': {'create': False},
                'view_mode': 'tree,form,kanban',
                'target': 'current'
            }

    def action_view_po_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender Bills',
            'res_model': 'account.move',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id, 'default_move_type': 'in_invoice'},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_multiple_vendor_bid(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender Bidding Line',
            'res_model': 'tender.bidding.line',
            'domain': [('tender_id', '=', self.id)],
            'context': {
                'default_tender_id': self.id,
                'search_default_group_by_qualified': 1,
                'expand': 1
            },
            'view_mode': 'tree,form',
            'target': 'current'
        }

    def action_view_multiple_po_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current'
        }

    # Scheduler
    @api.model
    def action_bid_close(self):
        today_date = fields.Date.today()
        record = self.env['tender.information'].search([('stage', '=', 'bid_submission')])
        bid = self.env['tender.bidding'].search([('qualify_status', '=', 'qualified'), ('stage', '=', 'bid')])
        for data in record:
            if data.bid_end_date == today_date:
                for rec in bid:
                    if rec.tender_id.id == data.id:
                        data.stage = 'bid_evaluation'
                        rec.stage = "bid_close"


class TenderInfoLine(models.Model):
    _name = 'tender.info.line'
    _description = "Tender Information Line"
    _rec_name = 'product_id'
    _order = 'sequence'

    product_id = fields.Many2one('product.product')
    code = fields.Char(related="product_id.default_code", string="Code", translate=True)
    name = fields.Text(string="Description", translate=True)
    qty = fields.Float(string="Qty.", default=1)
    uom_id = fields.Many2one(related="product_id.uom_po_id", string="Unit of Measure")
    tender_id = fields.Many2one('tender.information', string="Tender")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    sequence = fields.Integer()

    @api.onchange('product_id')
    def _onchange_product_desc(self):
        for rec in self:
            rec.name = rec.product_id.name


class TenderDocumentLine(models.Model):
    _name = 'tender.document.line'
    _description = "Tender Documents"
    _rec_name = 'document_type_id'

    document_type_id = fields.Many2one('document.type', domain="[('type','=','tender')]", string="Document Type")
    date = fields.Date(string="Date", default=fields.Date.today())
    note = fields.Text(string="Note", translate=True)
    document = fields.Binary(string='Documents', required=True)
    file_name = fields.Char(string='File Name', translate=True)
    tender_id = fields.Many2one('tender.information')
