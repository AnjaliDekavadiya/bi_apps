# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging


_logger = logging.getLogger(__name__)
from odoo.tools import html2plaintext
from odoo.exceptions import UserError, ValidationError



class JobCostSheet(models.Model):
    _inherit = 'job.cost.sheet'

    billable_method = fields.Selection(
        [('option_1', 'Based On Actual Purchase Qty'), ('option_2', 'Based On Actual Vendor Bill Qty'),
         ('option_3', 'Based Manual Invoice')], 'Customer Invoice Billable Method', default='option_1')
    invoice_count = fields.Integer(compute="get_invoice_count", string="Count", copy=False)

    def get_invoice_count(self):
        c_list = []
        invoice_ids = self.env['account.move'].search([('job_cost_id', '=', self.id)])
        for i in invoice_ids:
            c_list.append(i.id)
        self.invoice_count = len(c_list)

    def action_view_invoice_1(self):
        action = self.env.ref('account.action_move_out_invoice_type')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('job_cost_id', '=', self.id), ('move_type', '=', 'out_invoice')]
        tree_view_id = self.env.ref('account.invoice_tree', False)
        form_view_id = self.env.ref('account.invoice_form', False)
        result['views'] = [(tree_view_id and tree_view_id.id or False, 'tree'),
                           (form_view_id and form_view_id.id or False, 'form')]
        return result

    def action_view_invoice_customer(self):
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('job_cost_id', '=', self.id), ('move_type', '=', 'out_invoice')],
        }

    def unlink(self):
        if self.invoice_count > 0:
            raise ValidationError(_("You Cannot Delete This Record Its Invoice is already Generated"))
        return super(JobCostSheet, self).unlink()


class JobCostLine(models.Model):
    _inherit = "job.cost.line"

    actual_vendor_bill_qty = fields.Float(compute="_compute_vendor_bill_quantity", string='Actual Vendor Bill Quantity',
                                          default=0.0)

    def _compute_vendor_bill_quantity(self):
        for line in self:
            qty = 0
            invoice_line_ids = self.env['account.move.line'].search(
                [('product_id', '=', line.product_id.id), ('move_id.state', '!=', 'draft'),
                 ('move_id.move_type', '=', 'in_invoice')])
            for invoice in invoice_line_ids:
                if line.product_id.id == invoice.product_id.id:
                    if invoice.job_cost_sheet_id.id in [line.material_job_cost_sheet_id.id,
                                                        line.overhead_job_cost_sheet_id.id]:
                        if invoice.job_cost_sheet_id.id != False:
                            qty += invoice.quantity
            line.actual_vendor_bill_qty = qty


class Accountmove(models.Model):
    _inherit = "account.move"

    job_cost_id = fields.Many2one('job.cost.sheet', string='Job Cost')
