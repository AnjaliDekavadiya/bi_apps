# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

class JobCostSheetWizard(models.TransientModel):
    _name = 'job.cost.sheet.wizard'
    _description = "Job costing wizard"
    
    @api.model
    def default_get(self, fields):
        rec = super(JobCostSheetWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_id = context.get('active_id')
        if active_id:
            invoice = self.env['job.cost.sheet'].browse(active_id)
            rec.update({'partner_id': invoice.job_issue_customer_id.id})
        return rec
    
    material_include = fields.Boolean(string='Include Material Lines')
    labour_include = fields.Boolean(string='Include Labour Lines')
    overhead_include = fields.Boolean(string='Include Overhead Lines')
    partner_id = fields.Many2one('res.partner',string='Customer')
    invoice_date = fields.Date(string='Invoice Date',default=datetime.now().date())
    
    def action_invoice_create(self):
        record_id = self._context.get('active_id')
        your_class_records = self.env['job.cost.sheet'].browse(record_id)
        account = self.env['account.account'].search([('account_type','=','asset_receivable')],limit=1)
        acc = self.env['account.account'].search([('account_type','=','income')],limit=1)
        for res in self:
            invoice_id = self.env['account.move'].create({
                'partner_id' : res.partner_id.id,
                'invoice_date' : res.invoice_date,
                'job_cost_id':your_class_records.id,
                'job_cost_sheet_id': your_class_records.id,
                'move_type': 'out_invoice',
                'analytic_id': your_class_records.analytic_ids.id,
            })
            if not res.material_include and not res.labour_include and not res.overhead_include:
                raise ValidationError("Sorry !!! please select any one option for create invoice")
            if res.material_include:
                for line in your_class_records.material_job_cost_line_ids:
                    if your_class_records.billable_method == 'option_1':
                        newopt1 = self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id' : invoice_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_purchase_qty,
                            'account_id':acc.id,
                        })

                    if your_class_records.billable_method == 'option_2':
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id' : invoice_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_vendor_bill_qty,
                            'account_id':acc.id,
                            'price_unit':line.unit_price,
                        })
                        
                    if your_class_records.billable_method == 'option_3':
                        if line.quantity - line.invoiced_qty == 0:
                            raise ValidationError("Sorry !!! There is no have any material quantity invoice ")
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id' : invoice_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'product_uom_id' : line.uom_id.id,
                            'quantity' : line.quantity - line.invoiced_qty,
                            'account_id':acc.id,
                            'price_unit':line.unit_price,
                        })
                        
            if res.labour_include:
                for line in your_class_records.labour_job_cost_line_ids:
                    if line.quantity - line.invoiced_qty == 0:
                        raise ValidationError("Sorry !!! There is no have any labour quantity invoice ")
                    self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'move_id' : invoice_id.id,
                        'name' : line.description,
                        'product_id' : line.product_id.id,
                        'quantity': line.quantity - line.invoiced_qty,
                        'product_uom_id': line.uom_id.id,
                        'account_id':acc.id,
                        'price_unit':line.unit_price,
                    })

            if res.overhead_include:
                for line in your_class_records.overhead_job_cost_line_ids:
                    if your_class_records.billable_method == 'option_1':
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id' : invoice_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_purchase_qty,
                            'account_id':acc.id,
                            'price_unit':line.unit_price,
                        })
                        
                    if your_class_records.billable_method == 'option_2':
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id' : invoice_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_vendor_bill_qty,
                            'account_id':acc.id,
                            'price_unit':line.unit_price,
                        })
                    if your_class_records.billable_method == 'option_3':
                        if line.quantity - line.invoiced_qty == 0:
                            raise ValidationError("Sorry !!! There is no have any overhead quantity invoice ")
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'move_id' : invoice_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'account_id':acc.id,
                            'product_uom_id': line.uom_id.id,
                            'price_unit':line.unit_price,
                            'quantity': line.quantity - line.invoiced_qty,
                        })

