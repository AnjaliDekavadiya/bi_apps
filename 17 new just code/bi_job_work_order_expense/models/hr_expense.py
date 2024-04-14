# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    hr_expense_id = fields.Many2one('hr.expense') 

class hr_expense(models.Model):
    _inherit = 'hr.expense'

    project_id  =  fields.Many2one('project.project','Project')
    job_order_id = fields.Many2one('job.order','Job')
    attachment_ids = fields.One2many('ir.attachment','hr_expense_id')

class project_project(models.Model):
    _inherit = 'project.project'

    def _get_number_of_expenses_sheet(self):
        for project in self:
            list_exp_sheet_ids  = []
            expense_sheet_ids = self.env['hr.expense.sheet'].search([])
            for sheet in expense_sheet_ids:
                flag  = False
                for line in sheet.expense_line_ids:
                    if line.project_id.id == project.id:    
                        flag = True
                    else:
                        flag = False
                if flag == True:
                    list_exp_sheet_ids.append(sheet.id)  
            project.count_of_expanse_sheet = len(list_exp_sheet_ids)
    
    def button_view_expenses_sheet(self):
        for project in self:
            list_exp_sheet_ids  = []
            expense_sheet_ids = self.env['hr.expense.sheet'].search([])
            for sheet in expense_sheet_ids:
                flag  = False
                for line in sheet.expense_line_ids:
                    if line.project_id.id == project.id:   
                        flag = True
                    else:
                        flag = False
                if flag == True:
                    list_exp_sheet_ids.append(sheet.id)  
        context = dict(self._context or {})
        return {
            'name': _('Expenses Sheet'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.sheet',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',list_exp_sheet_ids)],
            'context': context,
        }
    
    def _get_number_of_expenses(self):
        for project in self:
            expense_ids = self.env['hr.expense'].search([('project_id', '=', project.id)])            
            project.count_of_expanse = len(expense_ids)

    def button_view_expenses(self):
        exp_list  = []
        exp_ids = self.env['hr.expense'].search([('project_id', '=', self.id)])
        for exp in exp_ids:
            exp_list.append(exp.id)
        context = dict(self._context or {})
        return {
            'name': _('Expenses '),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',exp_list )],
            'context': context,
        }

    count_of_expanse =  fields.Integer('Expanse',compute='_get_number_of_expenses')
    count_of_expanse_sheet =fields.Integer('Expanse Sheet',compute='_get_number_of_expenses_sheet')

class job_order(models.Model):
    _inherit = 'job.order'

    def _get_number_of_expenses_sheet(self):
        for project in self:
            list_exp_sheet_ids  = []
            expense_sheet_ids = self.env['hr.expense.sheet'].search([])
            for sheet in expense_sheet_ids:
                flag  = False
                for line in sheet.expense_line_ids:
                    if line.job_order_id.id == self.id :    
                        flag = True
                    else:
                        flag = False
                if flag == True:
                    list_exp_sheet_ids.append(sheet.id) 
            project.count_of_expanse_sheet = len(list_exp_sheet_ids)
    
    def button_view_expenses_sheet(self):
        for project in self:
            list_exp_sheet_ids  = []
            expense_sheet_ids = self.env['hr.expense.sheet'].search([])
            for sheet in expense_sheet_ids:
                flag  = False
                for line in sheet.expense_line_ids:
                    if line.job_order_id.id == self.id :   
                        flag = True
                    else:
                        flag = False
                if flag == True:
                    list_exp_sheet_ids.append(sheet.id)  
        context = dict(self._context or {})
        return {
            'name': _('Expenses Sheet'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense.sheet',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',list_exp_sheet_ids)],
            'context': context,
        }
                    
    def _get_number_of_expenses(self):
        for project in self:
            expense_ids = self.env['hr.expense'].search([('project_id', '=', self.project_id.id),('job_order_id','=',self.id)])            
            project.count_of_expanse = len(expense_ids)

    def button_view_expenses(self):
        exp_list  = []
        exp_ids = self.env['hr.expense'].search([('project_id', '=', self.project_id.id),('job_order_id','=',self.id)])
        for exp in exp_ids:
            exp_list.append(exp.id)
        context = dict(self._context or {})
        return {
            'name': _('Expenses '),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in',exp_list )],
            'context': context,
        }

    count_of_expanse =  fields.Integer('Expanse',compute='_get_number_of_expenses')
    count_of_expanse_sheet =fields.Integer('Expanse Sheet',compute='_get_number_of_expenses_sheet')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
