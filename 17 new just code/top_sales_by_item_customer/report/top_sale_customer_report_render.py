# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date

class TopSaleCustomer(models.AbstractModel):
    _name = 'report.top_sales_by_item_customer.report_topsalecustomer'
    _description = 'TopSaleCustomer'
    
    @api.model
    #def render_html(self, docids, data=None):
    def _get_report_values(self, docids, data=None):   # odoo 11
        active_ids = data['context'].get('active_ids')
        report = self.env['ir.actions.report']._get_report_from_name('top_sales_by_item_customer.report_topsalecustomer')
        topsale_wizard_obj = self.env['topsalecustomer.report']
        sale_order_line_obj = self.env['sale.order.line']
        customer_obj = self.env['res.partner']
        topsale_wizard_rec = topsale_wizard_obj.browse(active_ids)

        user_ids =  []
        
        start_date = datetime.date(datetime.strptime(str(topsale_wizard_rec.start_date), "%Y-%m-%d"))
        end_date = datetime.date(datetime.strptime(str(topsale_wizard_rec.end_date), "%Y-%m-%d"))
        customer_count = topsale_wizard_rec.top_sale_value
        
        start_date = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strftime(end_date, "%Y-%m-%d 23:59:59")
        
        if data.get(topsale_wizard_rec,False):
            user_ids = [topsale_wizard_rec][0]
        else:
            user_ids = docids

        lines=[] 

        query = """
         SELECT
             -- COUNT(line.id), line.order_partner_id, sum(so.amount_total_company_signed) as total
             COUNT(line.id), line.order_partner_id, sum(so.custom_amount_total_company_signed) as total
          FROM
              sale_order_line as line
          LEFT JOIN 
              sale_order AS so
          ON
              line.order_id = so.id
         WHERE
             so.date_order >= '%s' AND
             so.date_order <= '%s' AND
             so.state IN ('sale','done')
        GROUP BY
            line.order_partner_id
      """
        self._cr.execute(query %(start_date,end_date))
        lines = self._cr.dictfetchall()
        count = []
        dict_line = {}
        for line in lines:
            line_count = line['total']
            customer_id = line['order_partner_id']
            dict_lines = {line_count : customer_id}
            dict_line.update(dict_lines)
            count.append(dict_line)
            
        number_of_lines = sorted(dict_line.items(),reverse=True)
        customer_ids_list=[]
            
        for customer_ids in number_of_lines[:customer_count]:
            customer = customer_obj.browse(customer_ids[1])
            customer_ids_list.append({'customer_id' : customer, 'amount' : customer_ids[0]})
            
        currency = self.env.user.company_id.currency_id
        docs = topsale_wizard_rec
        
        #docargs = {
        return {        # odoo 11
            'doc_ids': user_ids,
            'doc_model': 'topsalecustomer.report',
            'data': data,
            'customer_ids' : customer_ids_list,
            'currency' : currency,
            'docs': docs,
        }
        #return self.env['report'].render('top_sales_by_item_customer.report_topsalecustomer', docargs)
        
