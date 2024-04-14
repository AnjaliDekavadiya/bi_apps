'''
Created on Oct 24, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError

_states = {'draft' : [('readonly', False)]}

def relativeDelta(enddate, startdate):   
    if not startdate or not enddate:
        return relativedelta()
    startdate = fields.Datetime.from_string(startdate)
    enddate = fields.Datetime.from_string(enddate) + relativedelta(days=1)
    return relativedelta(enddate, startdate)

def delta_desc(delta):
    res = []
    if delta.years:
        res.append('%s Years' % delta.years)
    if delta.months:
        res.append('%s Months' % delta.months)
    if delta.days:
        res.append('%s Days' % delta.days)
    return ', '.join(res)

class EndOfService(models.Model):
    _name = 'hr.end_of_service'
    _description = 'End of Service'
    _inherit = ['approval.record','mail.thread','mail.activity.mixin']    
    
    name = fields.Char(string='Number', required=True, readonly = True, copy = False, default = _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required = True, readonly = True, domain =[('contract_ids', '!=', False)])
    date = fields.Date('End of Service Date', required=True, readonly=True)
    
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', readonly = True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', readonly = True)
    manager_id = fields.Many2one('hr.employee', related='employee_id.parent_id', readonly = True)
        
    reason_id = fields.Many2one('hr.end_of_service.reason', string='End of Service Reason', required = True, readonly = True)
    termination_reason_id = fields.Many2one('hr.end_of_service.termination_reason', string='Termination Reason', readonly = True)
    
    company_id = fields.Many2one('res.company', required=True, string='Company', default=lambda self: self.env.company)        
    comments = fields.Text()
    
    join_date = fields.Date('Join Date', compute='_calc_join_date', store = True)
    service_year = fields.Float('Total Service Years', compute='_calc_service_year', store = True)
    service_month = fields.Float('Total Service Months', compute='_calc_service_year', store = True)
    service_desc = fields.Char('Total Service', compute='_calc_service_year', store = True)
    
    unpaid_leave_month = fields.Float('Unpaid Leave Months', compute='_calc_service_year', store = True)
    unpaid_leave_desc = fields.Char('Unpaid Leave', compute='_calc_service_year', store = True)        
    
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', ondelete = 'restrict')
    
    amount = fields.Float(compute = '_calc_amount', store = True)
        
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.company_id != self.company_id:
            self.company_id = self.employee_id.company_id
            
    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):      
        for vals in vals_list:      
            vals['name']= self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code(self._name)
        return super(EndOfService, self).create(vals_list)
    
    @api.depends('payslip_id.line_ids.amount')
    def _calc_amount(self):
        for record in self:
            record.amount = record.mapped('payslip_id.line_ids').filtered(lambda line : line.code == 'NET').amount
            
    @api.depends('employee_id.contract_ids.date_start')
    def _calc_join_date(self):
        for record in self:
            date_start = record.mapped('employee_id.contract_ids.date_start')
            record.join_date = min(date_start) if date_start else False
    
    @api.depends('join_date', 'date', 'employee_id')
    def _calc_service_year(self):
        for record in self:                        
            unpaid_leave_delta = relativedelta()
            unpaid_leave_ids = self.env['hr.leave'].sudo().search([('employee_id','=', record.employee_id.id), 
                                                               ('state', '=', 'validate'), 
                                                               ('holiday_status_id.unpaid','=',True)])
            for leave_id in unpaid_leave_ids:
                unpaid_leave_delta += relativeDelta(leave_id.date_to, leave_id.date_from)
                
            delta = relativeDelta(record.date, record.join_date)
            record.service_desc = delta_desc(delta)
            
            if self.env['ir.config_parameter'].sudo().get_param('hr.end_of_service.unpaid_leave') == 'True':
                delta -= unpaid_leave_delta
                
            
            record.unpaid_leave_desc = delta_desc(unpaid_leave_delta)
            record.unpaid_leave_month = (unpaid_leave_delta.years * 12) + (unpaid_leave_delta.months) + (unpaid_leave_delta.days / 30.0)            
            
            service_month = (delta.years * 12) + (delta.months) + (delta.days / 30.0)
            service_year = service_month / 12.0
            record.service_year = service_year
            record.service_month = service_month
            
                            
    
    def unlink(self):
        if any(self.filtered(lambda record : record.state!='draft')):
            raise UserError(_('You can delete draft status only'))
        return super(EndOfService, self).unlink()                        
    
    
    def _on_approve(self):
        if not self.payslip_id:
            raise UserError(_('No Pay Slip'))
        if not self.payslip_id.state != 'done':
            self.payslip_id.action_payslip_done()
        super(EndOfService, self)._on_approve()
    
    
    def action_payslip(self):    
        if not self.payslip_id:
            date_from = fields.Date.from_string(self.date) + relativedelta(day=1)
            date_to = date_from + relativedelta(day=31)
            date_from = fields.Date.to_string(date_from)
            payslip = self.env['hr.payslip'].create({'employee_id' : self.employee_id.id, 
                                                             'date_from' : date_from, 
                                                             'date_to' : date_to,
                                                             'end_of_service_id' : self.id})
            payslip.onchange_employee()
            payslip.compute_sheet()
            self.write({'payslip_id' : payslip.id})
        return {
            'type' : 'ir.actions.act_window',
            'res_model' : 'hr.payslip',
            'name' : 'Pay slip',
            'res_id' : self.payslip_id.id,
            'view_mode' : 'form',
            }
        