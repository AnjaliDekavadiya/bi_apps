# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class BidSelection(models.Model):
    _name = 'bid.selection'
    _description = "Bid Selection"

    name = fields.Char(default="Bid Selection")
    bid_selection = fields.Selection([('qualified', 'Qualified'), ('legit_bid', 'Authenticate Bid'), ('both', 'Both')],
                                     default='legit_bid', string="Bid From")
    bid_id = fields.Many2one('tender.bidding', string="Bid")

    @api.onchange('bid_selection', 'bid_id')
    def _onchange_bid_selection_bid(self):
        active_id = self._context.get('active_id')
        tender_id = self.env['tender.information'].browse(active_id)
        all_bids = tender_id.tender_bid_ids.mapped('id')
        qualify_ids = []
        legit_ids = []
        for data in tender_id.tender_bid_ids:
            if data.qualify_status == "qualified":
                qualify_ids.append(data.id)
            if data.is_legit_bid:
                legit_ids.append(data.id)
        for rec in self:
            if rec.bid_selection == "qualified":
                return {'domain': {'bid_id': [('id', 'in', qualify_ids)]}}
            elif rec.bid_selection == "legit_bid":
                return {'domain': {'bid_id': [('id', 'in', legit_ids)]}}
            else:
                return {'domain': {'bid_id': [('id', 'in', all_bids)]}}

    def action_select_tender_bid(self):
        active_id = self._context.get('active_id')
        tender_id = self.env['tender.information'].browse(active_id)
        tender_id.write({
            'bid_id': self.bid_id.id,
        })
