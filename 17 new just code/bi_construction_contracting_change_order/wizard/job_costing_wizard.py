# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import html2plaintext

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
            invoice = self.env['account.move'].browse(active_id)
            rec.update({'partner_id': invoice.partner_id.id})
        return rec
    
    material_include = fields.Boolean(string='Include Material Lines')
    labour_include = fields.Boolean(string='Include Labour Lines')
    overhead_include = fields.Boolean(string='Include Overhead Lines')
    partner_id = fields.Many2one('res.partner',string='Customer')
    invoice_date = fields.Date(string='Invoice Date',default=datetime.now())
    
    
    def action_invoice_create(self):
        record_id = self._context.get('active_id')
        your_class_records = self.env['job.cost.sheet'].browse(record_id)
        account = self.env['account.account'].search([('internal_type','=','receivable')],limit=1)
        for res in self:
            move_id = self.env['account.move'].create({
                'partner_id' : res.partner_id.id,
                'date_invoice' : res.invoice_date,
                'job_cost_id':your_class_records.id,
            })
            if res.material_include:
                for line in your_class_records.material_job_cost_ids:
                    if your_class_records.billable_method == 'option_1':
                        self.env['account.move.line'].create({
                            'move_id' : move_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_purchase_qty,
                            'account_id':account.id,
                            'price_unit':line.unit_price,
                        })
                    if your_class_records.billable_method == 'option_2':
                        self.env['account.invoice.line'].create({
                            'move_id' : move_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_vendor_bill_qty,
                            'account_id':account.id,
                            'price_unit':line.unit_price,
                        })
                    if your_class_records.billable_method == 'option_3':
                        self.env['account.invoice.line'].create({
                            'move_id' : move_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'account_id':account.id,
                            'price_unit':line.unit_price,
                        })
            if res.labour_include:
                for line in your_class_records.labour_job_cost_ids:
                    self.env['account.invoice.line'].create({
                        'move_id' : move_id.id,
                        'name' : line.description,
                        'product_id' : line.product_id.id,
                        'quantity':line.actual_timesheet_hours,
                        'account_id':account.id,
                        'price_unit':line.unit_price,
                    })
            if res.overhead_include:
                for line in your_class_records.overhead_job_cost_ids:
                    if your_class_records.billable_method == 'option_1':
                        self.env['account.invoice.line'].create({
                            'move_id' : move_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_purchase_qty,
                            'account_id':account.id,
                            'price_unit':line.unit_price,
                        })
                    if your_class_records.billable_method == 'option_2':
                        self.env['account.invoice.line'].create({
                            'move_id' : move_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'quantity':line.actual_vendor_bill_qty,
                            'account_id':account.id,
                            'price_unit':line.unit_price,
                        })
                    if your_class_records.billable_method == 'option_3':
                        self.env['account.invoice.line'].create({
                            'move_id' : move_id.id,
                            'name' : line.description,
                            'product_id' : line.product_id.id,
                            'account_id':account.id,
                            'price_unit':line.unit_price,
                        })
