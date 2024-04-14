# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models


class CourierHistoryReport(models.AbstractModel):
    _name = 'report.dev_courier_management.cr_req_history_tmpl'

    def get_courier_details(self, wizard_id):
        order_ids = self.env['dev.courier.request'].search(
            [('registration_date', '>=', wizard_id.start_date), ('registration_date', '<=', wizard_id.end_date)],
            order='id desc')
        if order_ids:
            return order_ids
        else:
            return False

    def _get_report_values(self, docids, data=None):
        docs = self.env['dev.courier.request.history'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'dev.courier.request.history',
            'get_courier_details': self.get_courier_details,
            'docs': docs,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
