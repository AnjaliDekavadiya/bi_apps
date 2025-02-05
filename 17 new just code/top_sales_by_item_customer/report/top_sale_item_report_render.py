# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date

class TopSaleItems(models.AbstractModel):
    _name = 'report.top_sales_by_item_customer.report_topsaleitem'
    _description = 'TopSaleItems'
    
    @api.model
    #def render_html(self, docids, data=None):
    def _get_report_values(self, docids, data=None):   # odoo 11
        report = self.env['ir.actions.report']._get_report_from_name('top_sales_by_item_customer.report_topsaleitem')
        active_ids = data['context'].get('active_ids')
        topsale_wizard_obj = self.env['topsaleitem.report']
        topsale_wizard_rec = topsale_wizard_obj.browse(active_ids)
        sale_order_line_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']

        user_ids =  []
        
        start_date = datetime.date(datetime.strptime(str(topsale_wizard_rec.start_date), "%Y-%m-%d"))
        end_date = datetime.date(datetime.strptime(str(topsale_wizard_rec.end_date), "%Y-%m-%d"))
        product_count = topsale_wizard_rec.top_sale_value
        
        start_date = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strftime(end_date, "%Y-%m-%d 23:59:59")
        
        sale_order_date = sale_order_line_obj.order_id
        if data.get(topsale_wizard_rec,False):
            user_ids = [topsale_wizard_rec][0]
        else:
            user_ids = docids
        user_id = topsale_wizard_obj._context['uid']

        lines=[] 

        query = """
         SELECT
             COUNT(line.id),line.product_id,SUM(line.product_uom_qty) as quantity
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
            line.product_id
      """
        self._cr.execute(query %(start_date,end_date))
        lines = self._cr.dictfetchall()
        count = []
        dict_line = {}
        for line in lines:
            product_quantity = line['quantity']
            product_id = line['product_id']
            dict_lines = {product_quantity : product_id}
            dict_line.update(dict_lines)
            count.append(dict_line)
            
        number_of_lines = sorted(dict_line.items(),reverse=True)
        product_ids_list=[]
            
        for product_ids in number_of_lines[:product_count]:
            product = product_obj.browse(product_ids[1])
            product_ids_list.append({'product_id' : product, 'qty' : int(product_ids[0])})
            
        docs = topsale_wizard_rec
        #docargs = {
        return { # doo11 
            'doc_ids': user_ids,
            'doc_model': 'topsaleitem.report',
            'data': data,
            'products' : product_ids_list,
            'docs': docs,
        }
        #return self.env['report'].render('top_sales_by_item_customer.report_topsaleitem', docargs)
        
