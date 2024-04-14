# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
import secrets
import xlwt
import base64
from odoo import fields, api, models
from io import BytesIO
from odoo.exceptions import UserError, ValidationError


class TenderBidding(models.Model):
    _name = 'tender.bidding'
    _description = "Tender Bidding"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "total_amount asc"

    name = fields.Char(string='Name',
                       copy=False,
                       default=lambda self: ('New'),
                       translate=True)
    date = fields.Date(string="Date", default=fields.Date.today())
    stage = fields.Selection([('pre_qualification', 'Pre Qualification'),
                              ('bid', 'Bid'),
                              ('bid_close', 'Bid Close'),
                              ('won', 'Won'),
                              ('lost', 'Lost')],
                             default="pre_qualification", tracking=True)
    qualify_status = fields.Selection([('qualified', 'Qualified'),
                                       ('disqualified', 'Disqualified')],
                                      string="Qualify Status",
                                      tracking=True)
    is_qualified_for_bid = fields.Boolean(string="Qualified for Bid")
    vendor_id = fields.Many2one('res.partner',
                                string="Vendor",
                                domain="[('is_vendor','=',True)]")
    vendor_tender_category_ids = fields.Many2many('tender.type',
                                                  related="vendor_id.tender_category_ids")
    tender_id = fields.Many2one('tender.information',
                                string="Tender",
                                domain="[('stage','=','bid_submission'),('tender_type_id','in',vendor_tender_category_ids)]")
    dis_qualified_reason = fields.Html(string="Reason For Disqualified")
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  string='Currency')
    rank = fields.Integer(string="Rank", compute="_compute_vendor_rank")
    is_legit_bid = fields.Boolean(string="Authentic bid",
                                  store=True,
                                  compute="_compute_bid_legit")
    type = fields.Selection(related="tender_id.type", required=True)
    allow_edit = fields.Selection([('edit_request', 'Edit Request'),
                                   ('request_approve', 'Request Approve'),
                                   ('draft', 'Draft')],
                                  string="Allow Edit", tracking=True)
    edit_request = fields.Boolean()
    responsible_id = fields.Many2one('res.users',
                                     string="Responsible User ",
                                     tracking=True)
    allow_resubmit = fields.Boolean()

    # Total & Count
    total_amount = fields.Monetary(string="Total",
                                   compute="_compute_bid_total",
                                   store=True)

    # One2many
    bid_document_ids = fields.One2many('bid.document.line',
                                       'bidding_id',
                                       string='Bid Documents')
    bidding_line_ids = fields.One2many('tender.bidding.line',
                                       'tender_bidding_id',
                                       string="Biding Line")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'tender.bid') or 'New'
        res = super(TenderBidding, self).create(vals_list)
        return res

    # Constrain
    @api.constrains('bidding_line_ids')
    def _check_product_id(self):
        for record in self.bidding_line_ids:
            if not record.display_type:
                duplicates = self.bidding_line_ids.filtered(
                    lambda r: r.id != record.id and r.product_id.id == record.product_id.id)
                if duplicates:
                    raise ValidationError("Product Already Added !")

    # Onchange
    @api.onchange('tender_id')
    def _onchange_tender_details(self):
        for rec in self:
            lines = []
            if rec.tender_id:
                rec.bidding_line_ids = [(5, 0, 0)]
                for data in rec.tender_id.tender_order_line:
                    lines.append((0, 0, {
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'qty': data.qty,
                        'display_type': data.display_type,
                        'sequence': data.sequence,
                        'product_from_tender': True
                    }))
                rec.bidding_line_ids = lines

    # Compute
    @api.depends('bidding_line_ids')
    def _compute_bid_total(self):
        for rec in self:
            total = 0.0
            if rec.bidding_line_ids:
                for data in rec.bidding_line_ids:
                    total = total + data.total
            rec.total_amount = total

    @api.depends('tender_id', 'total_amount')
    def _compute_vendor_rank(self):
        for rec in self:
            rank = 0
            sorted_records = self.search(
                [('tender_id', '=', rec.tender_id.id),
                 ('qualify_status', '=', 'qualified')],
                order='total_amount asc').mapped('id')
            if rec.id in sorted_records:
                rank = sorted_records.index(rec.id) + 1
            rec.rank = rank

    @api.depends('bidding_line_ids', 'qualify_status', 'bidding_line_ids.price')
    def _compute_bid_legit(self):
        bidding = self.env['tender.bidding.line'].search(
            [('tender_bidding_id', '=', self.id), ('display_type', '=', False)]).mapped('price')
        for rec in self:
            if rec.qualify_status == "qualified":
                if 0 in bidding:
                    rec.is_legit_bid = False
                else:
                    rec.is_legit_bid = True
            else:
                rec.is_legit_bid = False

    # Button
    def action_disqualified_bid(self):
        self.stage = "lost"
        self.qualify_status = "disqualified"
        self.responsible_id = self.env.user.id

    def action_pre_qualification(self):
        if self.allow_resubmit:
            self.stage = 'pre_qualification'

    def action_request_approve(self):
        self.allow_edit = 'request_approve'
        self.edit_request = False
        if self.type == "multiple_vendor":
            self._onchange_tender_details()
        self.send_edit_request_approve_mail(self.id)

    def action_qualified_bid(self):
        if self.bid_document_ids:
            self.qualify_status = "qualified"
            self.stage = "bid"
            mail_template = self.env.ref(
                'tk_tender_management.qualified_vendor_mail_template')
            self.allow_edit = 'request_approve'
            self.edit_request = False
            self.responsible_id = self.env.user.id
            if mail_template:
                mail_template.send_mail(self.id, force_send=True)
        else:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': 'Attach documents for Qualified or Disqualify Vendor',
                    'sticky': False,
                }
            }
            return message

    def send_edit_request_mail(self, id):
        mail_template = self.env.ref(
            'tk_tender_management.edit_request_mail_template')
        if mail_template:
            mail_template.send_mail(id, force_send=True)

    def send_edit_request_approve_mail(self, id):
        mail_template = self.env.ref(
            'tk_tender_management.edit_request_approved_mail_template')
        if mail_template:
            mail_template.send_mail(id, force_send=True)

    def action_export_tender_lines(self):
        bid_id = self.env['tender.bidding'].search([('id', '=', self.id)])
        attachment = self.env['ir.attachment'].sudo()
        attachment_id = self.export_tender_line_xls(bid_id, attachment)
        if attachment_id:
            report = {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment_id.id),
                'target': 'self',
                'nodestroy': False,
            }
            return report

    def export_tender_line_xls(self, bid_id, attachment):
        bidding_line_ids = bid_id.sudo().bidding_line_ids
        workbook = xlwt.Workbook(encoding='utf-8')
        heading = xlwt.easyxf(
            "align: vert centre, horiz centre;font: bold on,height 200")
        sheet_style = xlwt.easyxf("align: vert centre, horiz centre")
        sheet1 = workbook.add_sheet('Product', cell_overwrite_ok=True)
        sheet1.write(0, 0, 'Product', heading)
        sheet1.write(0, 1, 'Code', heading)
        sheet1.write(0, 2, 'Description', heading)
        sheet1.write(0, 3, 'Unit of Measure', heading)
        sheet1.write(0, 4, 'Quantity', heading)
        sheet1.write(0, 5, 'Your Price / Qty.', heading)
        c = 1
        for data in bidding_line_ids:
            if not data.display_type:
                sheet1.write(c, 0, data.product_id.name, sheet_style)
                sheet1.write(c, 1, data.code, sheet_style)
                sheet1.write(c, 2, data.name, sheet_style)
                sheet1.write(c, 3, data.uom_id.name)
                sheet1.write(c, 4, data.qty)
                sheet1.write(c, 5, 0.0)
                c = c + 1
        stream = BytesIO()
        workbook.save(stream)
        out = base64.encodebytes(stream.getvalue())
        attachment = attachment
        filename = "Bid Product" + ".xls"
        attachment_id = attachment.create(
            {'name': filename,
             'type': 'binary',
             'public': False,
             'access_token': secrets.token_urlsafe(12),
             'datas': out})
        return attachment_id


class BidDocumentLine(models.Model):
    _name = 'bid.document.line'
    _description = "Bid Document Line"

    document_type_id = fields.Many2one(
        'document.type', domain="[('type','=','bid')]", string="Document Type")
    date = fields.Datetime(string="Date", default=fields.Datetime.now())
    note = fields.Text(string="Note", translate=True)
    document = fields.Binary(string='Documents', required=True)
    file_name = fields.Char(string='File Name', translate=True)
    bidding_id = fields.Many2one('tender.bidding')


class TenderBiddingLine(models.Model):
    _name = 'tender.bidding.line'
    _description = "Tender Bidding Line"
    _rec_name = 'product_id'
    _order = "price asc"

    tender_bidding_id = fields.Many2one('tender.bidding')
    tender_id = fields.Many2one(
        related="tender_bidding_id.tender_id", store=True)
    qualify_status = fields.Selection(
        related="tender_bidding_id.qualify_status", store=True)
    vendor_id = fields.Many2one(related="tender_bidding_id.vendor_id")
    product_id = fields.Many2one('product.product')
    code = fields.Char(related="product_id.default_code",
                       string="Code", translate=True)
    name = fields.Text(string="Description", translate=True)
    qty = fields.Float(string="Qty.", default=1)
    uom_id = fields.Many2one(
        related="product_id.uom_po_id", string="Unit of Measure")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    sequence = fields.Integer()
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', string='Currency')
    price = fields.Monetary(string="Your Price / Qty.")
    total = fields.Monetary(string="Total Price",
                            compute="_compute_total_price")
    product_from_tender = fields.Boolean()
    selected_bid = fields.Boolean(string="Selected Bid")

    @api.onchange('product_id')
    def _onchange_product_desc(self):
        for rec in self:
            rec.name = rec.product_id.name

    @api.depends('price', 'qty')
    def _compute_total_price(self):
        for rec in self:
            rec.total = rec.price * rec.qty

    def action_select_bid(self):
        records = self.env['tender.bidding.line'].search(
            [('tender_id', '=', self.tender_id.id), ('product_id', '=', self.product_id.id),
             ('selected_bid', '=', True)])
        if not records:
            self.selected_bid = True
        else:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': 'This Product is already Selected',
                    'sticky': False,
                }
            }
            return message

    def action_deselect_bid(self):
        self.selected_bid = False
