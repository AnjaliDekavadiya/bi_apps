# -*- coding: utf-8 -*-

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

class TopSaleItem(models.TransientModel):
    _name = 'topsaleitem.report'
    _description = 'TopSaleItem'
    
    
    today = date.today()
    first_day = today.replace(day=1)
    last_day = date(today.year,today.month,1)+relativedelta(months=1,days=-1)
    
    start_date = fields.Date(
        'Start Date',
        required = True,
        default=first_day,
    )
    end_date = fields.Date(
        'End Date',
        required = True,
        default=last_day,
    )
    top_sale_value = fields.Integer(
        'Number of Products (Top)',
        default = lambda self:('100'),
        required = True,
    )
    
    # @api.multi #odoo13
    def top_sale_item(self):
        data = self.sudo().read()[0]
        #return self.env['report'].get_action(self, 'top_sales_by_item_customer.report_topsaleitem', data = data)
        return self.env.ref('top_sales_by_item_customer.top_sale_report_items').report_action(self, data=data, config=False)   # odoo 11
