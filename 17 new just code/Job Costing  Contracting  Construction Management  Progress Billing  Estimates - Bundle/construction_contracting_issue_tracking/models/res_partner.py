# -*- coding: utf-8 -*

from odoo import models, fields, api

class CustomerPrice(models.Model):
    _inherit = 'res.partner'

    product_id_construction = fields.Many2one(
        'product.product',
        string='Product',
    )
    
    #@api.multi
    # @api.depends('construction_ticket_ids')
    # def _ticket_count(self):
    #     for rec in self:
    #         rec.issue_ticket_count = len(rec.construction_ticket_ids)

    @api.depends('construction_ticket_ids')
    def _ticket_count(self):
        construction_ticket = self.env['construction.ticket']
        try:
            for record in self:
                try:
                    record.issue_ticket_count = construction_ticket.search_count([('partner_id', 'child_of', record.id)])
                except:
                    pass
        except:
            pass

    price_rate = fields.Float(
        string='Price / Rate (Company Currency)',
        default=0.0,
        copy=False,
    )

    issue_ticket_count = fields.Integer(
        compute = '_ticket_count',
        store=True,
     )
#    ticket_ids = fields.One2many(
#        'construction.ticket',
#        'partner_id',
#        string='Helpdesk Ticket',
#        readonly=True,
#    )
    construction_ticket_ids = fields.One2many(
        'construction.ticket',
        'partner_id',
        string='Construction Issue',
        readonly=True,
    )
     
    #@api.multi
    def show_ticket(self):
        self.ensure_one()
        # for rec in self:
        #     # res = self.env.ref('construction_contracting_issue_tracking.action_construction_ticket')
        #     # res = res.sudo().read()[0]
        res = self.env['ir.actions.act_window']._for_xml_id('construction_contracting_issue_tracking.action_construction_ticket')
        res['domain'] = str([('partner_id','=',self.id)])
        return res
