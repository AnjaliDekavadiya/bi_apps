# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class TenderDashboard(models.Model):
    _name = 'tender.dashboard'
    _description = "Tender Dashboard"

    name = fields.Char(string="Dashboard")

    @api.model
    def get_tender_stats(self):
        today_date = fields.Date.today()
        tender_obj = self.env['tender.information'].sudo()
        bid_obj = self.env['tender.bidding'].sudo()
        active_tender = tender_obj.search_count([('stage', '=', 'bid_submission')])
        tender_in_process = tender_obj.search_count([('stage', 'in', ['bid_evaluation', 'bid_selection'])])
        # Bid
        pre_qualification_bid = bid_obj.search_count([('stage', '=', 'pre_qualification')])
        pending_request = bid_obj.search_count([('edit_request', '=', True), ('allow_edit', '=', 'edit_request')])
        active_bid = bid_obj.search_count([('stage', '=', 'bid')])
        tender_type = [['Single Vendor for all Product', 'Product wise vendor'],
                       [tender_obj.search_count([('type', '=', 'single_vendor')]),
                        tender_obj.search_count([('type', '=', 'multiple_vendor')])]]
        pending_qualification = bid_obj.search_count(
            [('stage', '=', 'pre_qualification'), ('qualify_status', '=', False)])

        data = {
            'total_tender': tender_obj.search_count([]),
            'active_tender': active_tender,
            'tender_in_process': tender_in_process,
            'pre_qualification_bid': pre_qualification_bid,
            'pending_request': pending_request,
            'active_bid': active_bid,
            'tender_type': tender_type,
            'pending_qualification': pending_qualification,
            'tender_category': self.get_tender_category(),
            'tender_time_line': self.tender_time_line(),
        }
        return data

    def get_tender_category(self):
        category, tender = [], []
        categories = self.env['tender.type'].search([])
        if not categories:
            category, tender = [], []
        for c in categories:
            tender_type_data = self.env['tender.information'].sudo().search_count([('tender_type_id', '=', c.id)])
            tender.append(tender_type_data)
            category.append(c.name)
        return [category, tender]

    def tender_time_line(self):
        tender = []
        tender_data = self.env['tender.information'].search([])
        for t in tender_data:
            if t.stage == 'bid_submission':
                tender.append({
                    'name': str(t.name),
                    'start_date': str(t.start_date),
                    'end_date': str(t.end_date),
                })
        return tender
