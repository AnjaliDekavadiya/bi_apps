# -*- coding: utf-8 -*-

from odoo import models, fields


class LaundryBusinessServiceCustom(models.Model):
    _inherit = "laundry.business.service.custom"

    def show_laundry_meetings(self):
        self.ensure_one()
        res = self.env.ref('calendar.action_calendar_event')
        res = res.sudo().read()[0]
        res['domain'] = str([('laundry_request_custom_id', '=', self.id)])
        return res

    collection_user_id = fields.Many2one(
        'res.users',
        string='Collection User',
        copy=True,
    )
    delivery_user_id = fields.Many2one(
        'res.users',
        string='Delivery User',
        copy=True,
    )