# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    reference = fields.Char('Reference')

class JobOrder(models.Model):
    _inherit = 'job.order'

    customer_id = fields.Many2one('res.partner','Website Customer')
    customer_name = fields.Char('Website Customer Name')
    customer_email = fields.Char('Website Customer Email')
    customer_phone = fields.Char('Website Customer Phone')
    job_order_count  =  fields.Integer('Invoices', compute='attachment_on_job_order_button')

    def _get_attachment_count(self):
        for order in self:
            attachment_ids = self.env['ir.attachment'].search([('job_order_id','=',order.id)])
            order.attachment_count = len(attachment_ids)
        
    def attachment_on_job_order_button(self):
        self.ensure_one()
        return {
            'name': 'Attachment.Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('job_order_id', '=', self.id)],
        }
    
class ir_attachment(models.Model):
    _inherit='ir.attachment'

    job_order_id  =  fields.Many2one('job.order', 'Job Order')

class Website(models.Model):

    _inherit = "website"
    
    def get_job_order_details(self):            
        partner_brw = self.env['res.users'].browse(self._uid)
        job_order_ids = self.env['job.order'].search([('customer_id','=',partner_brw.partner_id.id)])
        return job_order_ids

    def get_project_details_for_job_order(self):            
        project_ids = self.env['project.project'].search([])
        return project_ids
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
