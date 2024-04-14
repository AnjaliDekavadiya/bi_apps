# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##########################################################################

from odoo import fields, models, api
from datetime import date


class RequestHistory(models.TransientModel):
    _name = 'dev.courier.request.history'
    _description = 'Request History Report'

    def print_pdf(self):
        return self.env.ref('dev_courier_management.menu_cr_req_history_tmpl').report_action(self)

    start_date = fields.Date(string='Start Date', required=True, default=date.today())
    end_date = fields.Date(string='End Date', required=True, default=date.today())

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: