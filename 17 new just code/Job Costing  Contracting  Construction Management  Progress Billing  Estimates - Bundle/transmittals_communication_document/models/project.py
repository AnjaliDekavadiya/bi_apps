# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Project(models.Model):
    _inherit = 'project.project'
    
    transmittion_ids = fields.One2many(
        'transmittal.document',
        'project_id',
        string='Transmittal Documents',
    )
    transmittal_document_count = fields.Integer(
        compute='_compute_transmittal_documents', 
        string='Transmittal Document Count'
    )
    
    # @api.multi
    @api.depends('transmittion_ids')
    def _compute_transmittal_documents(self):
        for rec in self:
            rec.transmittal_document_count = len(rec.transmittion_ids)
    
    # @api.multi
    def action_transmittal_documents(self):
        self.ensure_one()
        # action = self.env.ref('transmittals_communication_document.action_transmittal_document').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('transmittals_communication_document.action_transmittal_document')
        action['domain'] = [('project_id','=', self.id)]
        return action


class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    transmittion_ids = fields.One2many(
        'transmittal.document',
        'job_order_id',
        string='Transmittal Documents',
    )
    transmittal_document_count = fields.Integer(
        compute='_compute_transmittal_documents', 
        string='Transmittal Document Count'
    )
    
    # @api.multi
    @api.depends('transmittion_ids')
    def _compute_transmittal_documents(self):
        for rec in self:
            rec.transmittal_document_count = len(rec.transmittion_ids)
    
    # @api.multi
    def action_jobordertransmittal_documents(self):
        self.ensure_one()
        # action = self.env.ref('transmittals_communication_document.action_transmittal_document').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('transmittals_communication_document.action_transmittal_document')
        action['domain'] = [('job_order_id','=', self.id)]
        return action
    