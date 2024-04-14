# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import html2plaintext
from odoo.exceptions import UserError, ValidationError


class RequestInformation(models.Model):
    _name = "request.information"
    _description ="Request Information"
    _rec_name = 'sequence'
    _inherit = ['mail.thread']
    
    @api.model 
    def default_get(self, flds): 
        result = super(RequestInformation, self).default_get(flds)
        stage_nxt1 = self.env['ir.model.data']._xmlid_to_res_id('bi_website_project_request_for_information.rfi_stage') 
        result['stage_id'] = stage_nxt1
        return result
        
    def set_to_close(self):
        stage_obj = self.env['rfi.stage'].search([('name','=','Closed')])
        return self.write({'stage_id':stage_obj.id,'is_closed':True,'closed_date':datetime.now()})
        
    def _get_attachment_count(self):
        for rfi in self:
            attachment_ids = self.env['ir.attachment'].search([('rfi_info_id','=',rfi.id)])
            rfi.attachment_count = len(attachment_ids)
        
    def attachment_on_rfi_button(self):
        self.ensure_one()
        return {
            'name': 'Attachment.Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('rfi_info_id', '=', self.id)],
        }

    def _get_survey_count(self):
        for rfi in self:
            survey_ids = self.env['survey.survey'].search([('rfi_id','=',rfi.id)])
            rfi.survey_count = len(survey_ids)
        
    def survey_on_rfi_button(self):
        self.ensure_one()
        return {
            'name': 'Survey',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'res_model': 'survey.survey',
            'domain': [('rfi_id', '=', self.id)],
        }
        
                
    sequence = fields.Char(string='Sequence', readonly=True,copy=False,default=lambda self: self.env['ir.sequence'].get('request.information'))
    name = fields.Char('Name', required=True)
    request_type = fields.Many2one('rfi.type','Type')
    subject = fields.Many2one('rfi.subject','Subject')
    assign_to_id = fields.Many2one('res.users','Assign To')
    company_id = fields.Many2one('res.company','Company',index=True, default=lambda self: self.env.user.company_id)
    partner_id = fields.Many2one('res.partner','Customer/Supplier')
    phone = fields.Char('Phone')
    email = fields.Char('Email', size=128)
    rfi_team_id = fields.Many2one('rfi.team','RFI Team')
    project_id = fields.Many2one('project.project','Project')
    job_order_id = fields.Many2one('job.order','Job Order')
    job_cost_sheet_id = fields.Many2one('job.cost.sheet','Job Cost Sheet')
    team_leader_id = fields.Many2one('res.users','Team Leader')
    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    rfi_category_id = fields.Many2one('rfi.category','RFI Category')
    create_date = fields.Date('Create Date',default=datetime.now().date())
    is_closed = fields.Boolean(string="Is Closed",copy=False,readonly=True,default=False,)
    closed_date = fields.Date('Closed Date')
    description = fields.Text('Description')
    timesheet_ids = fields.One2many('account.analytic.line', 'request_id', 'Timesheets')
    rfi_survey_ids = fields.One2many('survey.survey', 'rfi_id', 'RFI Survey')
    rfi_answer = fields.Html('RFI Answer')
    stage_id = fields.Many2one('rfi.stage', 'Stage',copy=False,index=True)
    active = fields.Boolean('Active',default=True)
    attachment_count  =  fields.Integer('Attachments', compute='_get_attachment_count')
    customer_rating = fields.Selection([('1','Poor'), ('2','Average'), ('3','Good'),('4','Excellent')], 'Customer Rating')
    comment = fields.Text(string="Comment")
    survey_count  =  fields.Integer('Survey', compute='_get_survey_count')
    
    @api.onchange('job_cost_sheet_id')
    def onc_order(self):
        self.job_order_id = self.job_cost_sheet_id.job_order_id
        self.analytic_account_id = self.job_cost_sheet_id.analytic_ids

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'email': False,
                'phone': False,
            })
            return
        values = {
            'email': self.partner_id.email,
            'phone': self.partner_id.phone,
        }
        self.update(values)

    @api.onchange('rfi_team_id')
    def onchange_team_id(self):
        res = {}
        if self.rfi_team_id:
            res = {'team_leader_id':self.rfi_team_id.team_leader_id}
        return {'value': res}

    @api.model_create_multi
    def create(self, vals_list):
        result = super(RequestInformation, self).create(vals_list)
        if result.closed_date and result.create_date:
            if result.closed_date < result.create_date:
                raise UserError(_('Close Date must be grater than Create Date'))

        return result

    def write(self, vals):
        result = super(RequestInformation, self).write(vals)

        if vals.get('closed_date'):
            if self.closed_date < self.create_date:
                raise UserError(_('Close Date must be grater than Create Date'))


        return result

class RfiSubject(models.Model):
    _name = 'rfi.subject' 
    _description ="RFI Subject" 
    
    name = fields.Char('Name')    

class RfiType(models.Model):
    _name = 'rfi.type' 
    _description = "RFI Type" 
    
    name = fields.Char('Name') 
                
class CrmTeam(models.Model):
    _inherit = 'crm.team'
    _description = "CRM Team"
    
    rfi_team_id = fields.Boolean("RFI Team")
        
class RfiTeam(models.Model):
    _name = 'rfi.team'
    _description = "RFI Team"
    _rec_name = 'team_id'


    name= fields.Char(string='Name')
    team_leader_id = fields.Many2one('res.users',string="Leader")
    team_id = fields.Many2one('crm.team', domain="[('rfi_team_id', '=', True)]", string="Team")
    team_member_ids = fields.Many2many('res.users',string="Team Members")
    is_team = fields.Boolean(string="Is Default Team?")
    
class RFIStage(models.Model):
    _name = "rfi.stage"
    _description = "Request Stage"
    
    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    fold = fields.Boolean(string="Folded in Form")

    _defaults = {
        'sequence': lambda *args: 1
    }    
    
class RfiCategory(models.Model):
    _name = 'rfi.category' 
    _description = " RFI Category" 
    
    name = fields.Char('Name')

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    request_id = fields.Many2one('request.information','Request Information')
    job_cost_sheet_id = fields.Many2one('job.cost.sheet','Job Cost Sheet')

class ir_attachment(models.Model):
    _inherit='ir.attachment'

    rfi_info_id  =  fields.Many2one('request.information', 'RFI Information')

class SurveySurvey(models.Model):
    _inherit='survey.survey'

    rfi_id  =  fields.Many2one('request.information', 'Request For Information')
    state = fields.Selection(selection=[
        ('draft', 'Draft'), ('open', 'In Progress'), ('closed', 'Closed')
    ], string="Survey Stage", default='draft', required=True,
        group_expand='_read_group_states')

        
class Website(models.Model):

    _inherit = "website"
    
    def get_rfi_category(self):            
        categ_ids = self.env['rfi.category'].search([])
        return categ_ids

    def get_rfi_details(self):            
        partner_brw = self.env['res.users'].browse(self._uid)
        rfi_ids = self.env['request.information'].search([('partner_id','=',partner_brw.partner_id.id)])
        return rfi_ids        
    
        
