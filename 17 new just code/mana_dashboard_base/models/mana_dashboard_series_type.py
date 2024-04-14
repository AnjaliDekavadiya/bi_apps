
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ManaDashboardSeriesType(models.Model):
    '''
    Mana Dashboard Series Type
    '''
    _name = 'mana_dashboard.series_type'
    _description = 'Mana Dashboard Series Type'

    name = fields.Char(string='name')
