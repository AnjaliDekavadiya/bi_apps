# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    project_custom_id = fields.Many2one(
        'project.project',
        string='Project',
        copy=False,
    )
    partner_custom_id = fields.Many2one(
        'res.partner',
        string='Customer',
        copy=False,
    )

    def action_event_organizor_project_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project.open_view_project_all_config')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_task_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project.act_project_project_2_project_task_all')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_job_costsheet_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('odoo_job_costing_management.action_job_costing')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_material_requisition_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('material_purchase_requisitions.action_material_purchase_requisition')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_sale_estimate_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('odoo_sale_estimates.action_estimate')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_sale_order_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_purchase_order_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        action['domain'] = [('event_custom_id','=', self.id)]
        return action

    def action_event_organizor_accountmove_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('event_custom_id','=', self.id),('move_type','=','out_invoice')]
        return action

    def action_event_organizor_vendorbill_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        action['domain'] = [('event_custom_id','=', self.id),('move_type','=','in_invoice')]
        return action

    def action_event_calendar_meeting_custom(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('calendar.action_calendar_event')
        action.update({'context':{'default_event_custom_id':self.id}})
        action['domain'] = [('event_custom_id','=', self.id)]
        return action
