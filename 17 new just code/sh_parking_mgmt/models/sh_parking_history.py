# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class ParkingHistory(models.Model):

    _name = 'sh.parking.history'
    _description = 'Parking History'

    name = fields.Char(string='Qr no.',
                       readonly=True)

    sh_subslot_id = fields.Many2one(
        comodel_name='sh.parking.subslot', string='Slot')
    sh_partner_id = fields.Many2one(
        comodel_name='res.partner', string='Member Customer Name')
    sh_vehicle_id = fields.Many2one(
        comodel_name="sh.parking.vehicle", string="Vehicle")
    sh_check_in_time = fields.Datetime(
        string="Check in date time")
    sh_expected_check_out_time = fields.Datetime(
        string="Expected Check out date time")
    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    sh_check_out_time = fields.Datetime(string="Check out date time")
    sh_duration = fields.Float(
        string="Duration")
    sh_vehicle_no = fields.Char(string="Vehicle no")
    sh_membership_id = fields.Many2one(
        comodel_name='sh.parking.membership', string='Membership Name')
    sh_amount = fields.Monetary(
        string='Amount',currency_field='currency_id')
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, default=lambda self: self.env.company)
