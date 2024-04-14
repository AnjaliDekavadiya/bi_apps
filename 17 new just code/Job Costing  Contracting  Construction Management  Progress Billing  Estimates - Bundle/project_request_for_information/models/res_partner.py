# -*- coding: utf-8 -*

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    rfi_product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    #@api.multi
    @api.depends('rfi_request_information_ids')
    def _compute_rfi_ticket_count(self):
        for rec in self:
            rec.rfi_ticket_count = len(rec.rfi_request_information_ids)

    rfi_price_rate = fields.Float(
        string='Price / Rate (Company Currency)',
        default=0.0,
        copy=False,
    )
    rfi_ticket_count = fields.Integer(
        compute = '_compute_rfi_ticket_count',
        store=True,
     )
    rfi_request_information_ids = fields.One2many(
        'request.information',
        'partner_id',
        string='Request for Informations',
        readonly=True,
    )

    #@api.multi
    def action_rfi_show_ticket(self):
        self.ensure_one()
        # for rec in self:
        # res = self.env.ref('project_request_for_information.action_request_information')
        res = self.env['ir.actions.act_window']._for_xml_id('project_request_for_information.action_request_information')
        # res = res.sudo().read()[0]
        res['domain'] = str([('partner_id','=',self.id)])
        return res

    #@api.multi
    def action_view_rfi_request(self):
        self.ensure_one()
        # action = self.env.ref('project_request_for_information.action_request_information')
        action = self.env['ir.actions.act_window']._for_xml_id('project_request_for_information.action_request_information')
        # action = action.sudo().read()[0]
        action['domain'] = str([('partner_id','=',self.id)])
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
