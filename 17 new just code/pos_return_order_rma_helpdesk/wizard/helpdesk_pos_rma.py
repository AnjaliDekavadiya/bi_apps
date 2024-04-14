# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api,_

class POSHelpdeskRMACREATE(models.TransientModel):
    _name = 'pos.create.rma.helpdesk.wizard'
    _description = "POS Helpdesk RMA CREATE"

    @api.model
    def default_get(self, fields):
        res = super(POSHelpdeskRMACREATE, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'helpdesk.support':
            record = self.env[model].browse(active_id)
            res.update({
                'partner_id': record.partner_id,
                'pos_order_id' : record.cust_pos_order_id,
                'description':record.description,
            })
        return res

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required = True
    )
    pos_order_id = fields.Many2one(
        'pos.order',
        string='POS Order',
        required = True
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        readonly=True,
    )
    description = fields.Text(
        string="Reason"
    )
    reason_id = fields.Many2one(
        'return.reason',
        string='Return Reason',
        required = True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
        default=lambda self: self.env.user,
        required = True
    )
    
    def create_helpdesk_rma_order_custom(self):
        self.ensure_one()
        active_id = self._context.get('active_id')
        rma_vals = {
            'partner_id':self.partner_id.id,
            'posorder_id':self.pos_order_id.id,
            'is_pos_order' : True,
            'create_date':fields.date.today(),
            'company_id':self.company_id.id,
            'reason':self.description,
            'reason_id':self.reason_id.id,
            'salesperson_id':self.user_id.id,

        }
        rma_id = self.env['return.order'].create(rma_vals)
        action = self.env.ref('website_request_return_rma_odoo.action_return_repair_rma')
        result = action.sudo().read()[0]
        result['domain'] = [('id', '=', rma_id.id)]
        return result
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
   

     
        