# -*- coding: utf-8 -*-

from odoo import fields, models, api

class Meeting(models.Model):
    _inherit = 'calendar.event'
    
    custom_number = fields.Char(
        string="Appointment ID",
        readonly=True
    )
    custom_customer_name = fields.Many2one(
        'res.partner',
        string='Name',
        copy=False,
    )
    custom_email = fields.Char(
        string='Email',
        copy=False,
    )
    custom_phone = fields.Char(
        string='Phone',
        copy=False,
    )
    custom_slot = fields.Char(
        string='Time Slot',
        copy=False,
    )

    # @api.model
    # def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        # result = super(Meeting, self).create(vals)
        result = super(Meeting, self).create(vals_list)
        for record in result:
            record.custom_number = self.env['ir.sequence'].next_by_code('calendar.event')
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
