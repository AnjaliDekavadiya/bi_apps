# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    def _compute_courier_count(self):
        for rec in self:
            counter = rec.env['dev.courier.request'].search_count(['|', ('sender_id', '=', rec.id), ('receiver_id', '=', rec.id)])
            rec.courier_count = counter

    def view_courier_request(self):
        order_ids = self.env['dev.courier.request'].search(['|', ('sender_id', '=', self.id), ('receiver_id', '=', self.id)])
        action = self.env.ref('dev_courier_management.action_dev_courier_request').sudo().read()[0]
        if len(order_ids) > 1:
            action['domain'] = [('id', 'in', order_ids.ids)]
        elif len(order_ids) == 1:
            action['views'] = [(self.env.ref('dev_courier_management.view_dev_courier_request_form').id, 'form')]
            action['res_id'] = order_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    courier = fields.Boolean(string='Courier')
    courier_count = fields.Integer(string='Courier Counter', compute='_compute_courier_count')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: