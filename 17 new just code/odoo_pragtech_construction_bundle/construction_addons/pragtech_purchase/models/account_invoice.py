# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"
    _description = 'Account Invoice'

    @api.model
    def _default_project_wbs(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id'):
            return self.env['purchase.order'].browse(self._context.get('active_id')).project_wbs

    @api.model
    def _default_project(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id'):
            return self.env['purchase.order'].browse(self._context.get('active_id')).project_id

    @api.model
    def _default_stage(self):
        st_ids = self.env['stage.master'].search([('draft', '=', True)])
        if st_ids:
            for st_id in st_ids:
                return st_id.id

    project_id = fields.Many2one('project.project', 'Project', required=False,domain=[('approval_state','=','approve')])
    project_wbs_id = fields.Many2one('project.task', 'Project WBS Name', required=False, domain=[('is_wbs', '=', True), ('project_id', '!=', False)])
    grn_ids = fields.Many2many('stock.picking', 'picking_invoice_rel', 'invoice_id', 'picking_id', string="Picking Details")
    flag = fields.Boolean('Flag')
    stage_id = fields.Many2one('stage.master', 'Stage', readonly=True, copy=False)
    mesge_ids = fields.One2many('mail.messages', 'res_id', string='Massage', domain=lambda self: [('model', '=', self._name)], auto_join=True, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            existing_stage = []
            st_id = self.env['stage.master'].sudo().search([('draft', '=', True)])
            created_by = self.env['res.users'].browse(self._uid).name
            msg_ids = {
                'date': datetime.now(),
                'from_stage': None,
                'to_stage': st_id.id,
                'remark': 'Created by {}'.format(str(created_by)),
                'model': 'account.move'
            }
            existing_stage.append((0, 0, msg_ids))
            vals.update({'mesge_ids': existing_stage})

        return super(AccountInvoice, self).create(vals_list)

    def change_state(self, context={}):
        if context.get('copy') == True:
            self.flag = True
        else:
            view_id = self.env.ref('pragtech_purchase.approval_wizard_form_view_purchase').id
            return {
                'type': 'ir.actions.act_window',
                'key2': 'client_action_multi',
                'res_model': 'approval.wizard',
                'multi': 'True',
                'target': 'new',
                'views': [[view_id, 'form']],
            }

    def compute_picking(self):
        self.onchange_vendor_id()

    @api.onchange('partner_id', 'project_id', 'project_wbs_id')
    def onchange_vendor_id(self):
        return {
            'domain': {
                'grn_ids': [('project_id', '=', self.project_id.id), ('project_wbs', '=', self.project_wbs_id.id), ('partner_id', '=', self.partner_id.id), ('state', 'in', ['done'])]
            }
        }

    @api.onchange('grn_ids')
    @api.depends('grn_ids')
    def onchange_grn_ids(self):
        data_lst = []
        tax_ids = []

        for grn in self.grn_ids:
            purchase_obj = self.env['purchase.order'].search([('name', '=', grn.origin)])
            for moves in grn.move_ids:
                for line in moves.move_line_ids:
                    purchase_line = self.env['purchase.order.line'].search([('order_id', '=', purchase_obj.id), ('product_id', '=', line.product_id.id)])
                    for tax_id in purchase_line.taxes_id:
                        tax_ids.append(tax_id.id)

                    data = {
                        # 'purchase_id': grn.po_id.id,
                        'purchase_line_id': purchase_line.id,
                        'name': str(line.product_id.name),
                        'product_id': line.product_id.id,
                        # 'account_id': self.account_id.id,
                        'quantity': line.qty_done,
                        'product_uom_id': line.product_uom_id.id,
                        'price_unit': purchase_line.price_unit,
                        'tax_ids': [(6, 0, tax_ids)],
                        'picking_id': line.picking_id.id,
                        'partner_id': purchase_line.order_id.partner_id.id,
                        # 'project_id': purchase_line.order_id.project_id.id,
                        # 'project_wbs_id': purchase_line.order_id.project_id.id,
                    }
                    data_lst.append((0, 0, data))

        self.update({'invoice_line_ids': data_lst})


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"
    _description = "Account Invoice Line"

    remark = fields.Text('Remark')
    picking_id = fields.Many2one('stock.picking', string="Picking")

