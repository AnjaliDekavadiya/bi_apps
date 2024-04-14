# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import tools
from odoo import api, fields, models


class RequestAnalysisReport(models.Model):
    _name = 'dev.courier.request.analysis'
    _description = 'Courier Request Analysis Report'
    _auto = False

    name = fields.Char('Name')
    sender_id = fields.Many2one('res.partner')
    sender_name = fields.Char('Sender Name')
    sender_street = fields.Char('Sender Street')
    sender_street2 = fields.Char('Sender Street2')
    sender_city = fields.Char('Sender City')
    sender_state_id = fields.Many2one('res.country.state', string='Sender State')
    sender_country_id = fields.Many2one('res.country', string='Sender Country')
    sender_zip = fields.Char('Sender Zip')
    sender_mobile = fields.Char('Sender Mobile')
    sender_email = fields.Char('Sender Email')
    receiver_id = fields.Many2one('res.partner', string='Receiver')
    receiver_name = fields.Char('Sender Name')
    receiver_street = fields.Char('Street')
    receiver_street2 = fields.Char('Street2')
    receiver_city = fields.Char('City')
    receiver_state_id = fields.Many2one('res.country.state')
    receiver_country_id = fields.Many2one('res.country')
    receiver_zip = fields.Char('Zip')
    receiver_mobile = fields.Char('Receiver Mobile')
    receiver_email = fields.Char('Receiver Email')
    registration_date = fields.Date('Registration Date')
    delivery_date = fields.Date('Delivery Date')
    courier_type_id = fields.Many2one('dev.courier.type', string='Type')
    category_id = fields.Many2one('dev.courier.category', string='Category')
    priority_id = fields.Many2one('dev.courier.priority', string='Priority')
    total_km = fields.Integer('Kilometres')
    user_id = fields.Many2one('res.users', string='User')
    company_id = fields.Many2one('res.company', string='Company')
    currency_id = fields.Many2one('res.currency')
    state_id = fields.Many2one('dev.courier.stages', string='State')
    edi_distance_charge = fields.Monetary('Distance Charges')
    edi_additional_charge = fields.Monetary('Additional Charges')
    total_charge_amount = fields.Monetary('Total Charge')

    def _select(self):
        select_str = """ SELECT
                    min(cr.id) as id,
                    cr.name,
                    cr.sender_id,
                    cr.sender_name,
                    cr.sender_street,
                    cr.sender_street2,
                    cr.sender_city,
                    cr.sender_state_id,
                    cr.sender_country_id,
                    cr.sender_zip,
                    cr.sender_mobile,
                    cr.sender_email,
                    cr.receiver_id,
                    cr.receiver_name,
                    cr.receiver_street,
                    cr.receiver_street2,
                    cr.receiver_city,
                    cr.receiver_state_id,
                    cr.receiver_country_id,
                    cr.receiver_zip,
                    cr.receiver_mobile,
                    cr.receiver_email,
                    cr.registration_date,
                    cr.delivery_date,
                    cr.courier_type_id,
                    cr.category_id,
                    cr.priority_id,
                    cr.total_km,
                    cr.user_id,
                    cr.company_id,
                    cr.state_id,
                    cr.edi_distance_charge,
                    cr.total_charge_amount,
                    cr.edi_additional_charge
        """
        return select_str

    def _from(self):
        from_str = """dev_courier_request cr join res_partner cust on (cr.sender_id = cust.id)"""
        return from_str

    def _group_by(self):
        group_by_str = """ GROUP BY
                    cr.name,
                    cr.sender_id,
                    cr.sender_name,
                    cr.sender_street,
                    cr.sender_street2,
                    cr.sender_city,
                    cr.sender_state_id,
                    cr.sender_country_id,
                    cr.sender_zip,
                    cr.sender_mobile,
                    cr.sender_email,
                    cr.receiver_id,
                    cr.receiver_name,
                    cr.receiver_street,
                    cr.receiver_street2,
                    cr.receiver_city,
                    cr.receiver_state_id,
                    cr.receiver_country_id,
                    cr.receiver_zip,
                    cr.receiver_mobile,
                    cr.receiver_email,
                    cr.registration_date,
                    cr.delivery_date,
                    cr.courier_type_id,
                    cr.category_id,
                    cr.priority_id,
                    cr.total_km,
                    cr.user_id,
                    cr.company_id,
                    cr.state_id,
                    cr.edi_distance_charge,
                    cr.total_charge_amount,
                    cr.edi_additional_charge
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s ) %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
