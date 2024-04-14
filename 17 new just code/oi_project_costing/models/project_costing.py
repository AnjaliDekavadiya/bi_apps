'''
Created on Apr 22, 2019

@author: Zuhair Hammadi
'''

from odoo import models, fields, api


class ProjectCosting(models.Model):
    _name = 'project.costing'
    _description = _name
    _order = 'category_code,sequence,id'
    
    name = fields.Char('Description')    
    sequence = fields.Integer()
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', ondelete='restrict', index=True)    
    category_id = fields.Many2one('project.costing.category')    
    category_code = fields.Char(related='category_id.code', store=True)
    
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")    
    
    product_id = fields.Many2one('product.product')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')    
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", store=True, compute_sudo=True)        
        
    plan_qty = fields.Float('Plan Quantity')
    plan_price = fields.Monetary('Plan Price', group_operator='avg')
    plan_amount = fields.Monetary('Plan Amount', compute='_calc_plan_amount', store=True)
    plan_amount_display = fields.Monetary(compute='_calc_plan_amount_display')
    
    analytic_line_ids = fields.Many2many('account.analytic.line', compute='_calc_line_ids')
    actual_qty = fields.Float('Actual Quantity', compute='_calc_actual', store=True, compute_sudo=True)
    actual_price = fields.Monetary('Actual Price', compute='_calc_actual', store=True, compute_sudo=True, group_operator='avg')
    actual_amount = fields.Monetary('Actual Amount', compute='_calc_actual', store=True, compute_sudo=True)
    actual_amount_display = fields.Monetary(compute='_calc_actual_amount_display')
    
    parent_id = fields.Many2one('project.costing', compute='_calc_parent_id', store=True, compute_sudo=True)
    child_ids = fields.One2many('project.costing', 'parent_id')
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.name:
            self.name = self.product_id.name
        self.product_uom_id = self.product_id.uom_id
        self.plan_price = self.product_id.standard_price
    
    @api.depends('plan_qty', 'plan_price', 'child_ids')
    def _calc_plan_amount(self):
        for record in self:
            if record.child_ids:
                record.plan_amount = sum(record.mapped('child_ids.plan_amount'))
            else:
                record.plan_amount = record.plan_qty * record.plan_price
    
    @api.depends('plan_amount', 'display_type')
    def _calc_plan_amount_display(self):
        for record in self:
            if record.display_type:
                record.plan_amount_display = 0
            else:
                record.plan_amount_display = record.plan_amount
                
    @api.depends('actual_amount', 'display_type')
    def _calc_actual_amount_display(self):
        for record in self:
            if record.display_type:
                record.actual_amount_display = 0
            else:
                record.actual_amount_display = record.actual_amount
    
    @api.depends('child_ids')
    def _calc_plan_qty(self):
        for record in self:
            if record.child_ids:
                record.plan_qty = sum(record.mapped('child_ids.plan_qty'))
            
    @api.depends('child_ids')
    def _calc_plan_price(self):
        for record in self:
            if record.child_ids:
                lst = record.mapped('child_ids.plan_price')
                record.plan_price = lst and sum(lst) / len(lst)
                
    @api.depends('analytic_id.project_costing_ids')
    def _calc_parent_id(self):
        for record in self:
            if record.display_type:
                record.parent_id = False
                continue
            found = False
            parent_id = False
            for costing in record.analytic_id.project_costing_ids.sorted(reverse=True):
                if not found and costing != record:
                    continue
                if costing == record:
                    found = True
                    continue
                if costing.display_type == 'line_section':
                    parent_id = costing
                    break
            record.parent_id = parent_id
                
    @api.depends('analytic_id', 'child_ids')
    def _calc_line_ids(self):
        for record in self:
            if record.child_ids:
                record.analytic_line_ids = record.mapped('child_ids.analytic_line_ids')
                continue
            domain = [('account_id', '=', record.analytic_id.id), ('company_id', '=', record.company_id.id), ('product_id', '=', record.product_id.id)]
            record.analytic_line_ids = self.env['account.analytic.line'].search(domain)    

    @api.depends('analytic_id.project_line_ids.amount')
    def _calc_actual(self):
        for record in self:
            line_ids = record.analytic_line_ids
            record.actual_qty = abs(sum(line_ids.mapped('unit_amount')))
            record.actual_amount = -sum(line_ids.mapped('amount'))
            record.actual_price = abs(record.actual_qty and record.actual_amount / record.actual_qty)
    
    def _calc_plan(self):
        self._calc_plan_amount()
        self._calc_plan_qty()
        self._calc_plan_price() 
    
    def _update_parent_plan(self):
        self.exists().mapped('parent_id')._calc_plan()
        
    def _update_parent_actual(self):
        self.exists().mapped('parent_id')._calc_actual()
                        
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(ProjectCosting, self).create(vals_list)
        records._update_parent_plan()
        records._update_parent_actual()
        return records
    
    def write(self, vals):
        res = super(ProjectCosting, self).write(vals)
        self._update_parent_plan()
        self._update_parent_actual()
        return res
    
    def unlink(self):
        parent_ids = self.mapped('parent_id')
        res = super(ProjectCosting, self).unlink()
        parent_ids.exists()._calc_plan()
        parent_ids.exists()._update_parent_actual()
        return res
        
