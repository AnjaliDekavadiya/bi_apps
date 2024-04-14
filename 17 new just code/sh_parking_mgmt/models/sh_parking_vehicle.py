# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models


class Vehicle(models.Model):

    _name = 'sh.parking.vehicle'
    _description = 'Parking Vehicle'

    name = fields.Char(string='Vehicle Type', required=True)
