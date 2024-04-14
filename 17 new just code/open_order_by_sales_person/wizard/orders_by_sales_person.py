# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo.tools.misc import xlwt
import io
import base64
import datetime
import datetime, calendar
import time
from odoo import models, fields, api, _
from odoo.http import request
from dateutil.relativedelta import relativedelta

class ExportOrderbySalesPerson(models.TransientModel):
    _name = 'export.sale.order.user.wizard'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id.id,
        required=True,
    )
    start_date = fields.Date(
        string='Start Date', 
        required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)
        )
    )
    end_date = fields.Date(
        string='End Date', 
        required=True,
        default=lambda self: fields.Date.to_string((date.today() + relativedelta(months=+1, day=1, days=-1))
        )
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Sales Person',
    )

    # @api.multi
    def print_user_sale_order_excel(self):
        domain = []
        sale_obj = self.env['sale.order']
        # domain = [
        #     ('confirmation_date','>=',self.start_date),
        #     ('confirmation_date', '<=', self.end_date),
        #     ('state', '=','sale' ),
        # ]
        domain = [
            ('date_order','>=',self.start_date),
            ('date_order', '<=', self.end_date),
            ('state', '=','sale' ),
        ]
        product = self.env['product.product']
        if self.user_ids:
            domain.append(('user_id','in',self.user_ids.ids))
        
        sale_order = sale_obj.search(domain)
        workbook = xlwt.Workbook()
        title_style_comp = xlwt.easyxf('align: horiz center ; font: name Times New Roman,bold on, italic off, height 240; pattern: pattern solid, fore_colour gold;')
        title_style_comp_1 = xlwt.easyxf('align: horiz center ; font: name Times New Roman,bold on, italic off, height 240; pattern: pattern solid, fore_colour ice_blue;')
        title_style_comp_left = xlwt.easyxf('align: horiz center ; font: name Times New Roman,bold on, italic off, height 240;pattern: pattern solid, fore_colour gray25;')
        title_style1_table = xlwt.easyxf('align: horiz left ;font: name Times New Roman,bold on, italic off, height 190;')
        title_style = xlwt.easyxf('align: horiz center ;font: name Times New Roman,bold off, italic off, height 350')
        title_style2 = xlwt.easyxf('align: horiz left ;font: name Times New Roman, height 200')
        title_style1 = xlwt.easyxf('align: horiz left; font: name Times New Roman,bold off, italic off, height 190; borders: top double, bottom double, left double, right double;')
        title_style1_table_head = xlwt.easyxf('align: horiz center; font: name Times New Roman,bold on, italic off, height 200; borders: top double, bottom double, left double, right double;pattern: pattern solid, fore_colour light_turquoise;')
        title_style1_table_head1 = xlwt.easyxf('align: horiz left;font: name Times New Roman,bold on, italic off, height 200')
        title_style1_table_head2 = xlwt.easyxf('align: horiz center; font: name Times New Roman,bold on, italic off, height 200;pattern: pattern solid, fore_colour light_turquoise;')
        title_style1_consultant = xlwt.easyxf('align: horiz left; font: name Times New Roman,bold on, italic off, height 200; borders: top double, bottom double, left double, right double;')
        title_style1_table_head_center = xlwt.easyxf('align: horiz right ;font: name Times New Roman,bold on, italic off, height 190;pattern: pattern solid, fore_colour light_green;')
        title_style1_table_data = xlwt.easyxf('align: horiz left ;font: name Times New Roman,bold on, italic off, height 190;pattern: pattern solid, fore_colour light_green;')
        title_style1_table_data_sub = xlwt.easyxf('align: horiz left ;font: name Times New Roman,bold off, italic off, height 190')
        title_style1_table_data_sub_amount = xlwt.easyxf('align: horiz right ;font: name Times New Roman,bold off, italic off, height 190')
        title_style1_table_data_sub_balance = xlwt.easyxf('align: horiz left ;font: name Times New Roman,bold off, italic off, height 190')
        sheet_name = 'Open Orders by Sales Person'
        sheet = workbook.add_sheet(sheet_name)
        start_date = self.start_date
        end_date = self.end_date
        company_id = self.company_id
        sheet.write(0, 0,'Start Date ' , title_style_comp_left)
        sheet.write(1, 0,start_date.strftime('%d/%m/%Y'), title_style1_table)
        sheet.write(0, 1,'End Date ' , title_style_comp_left)
        sheet.write(1, 1,end_date.strftime('%d/%m/%Y'), title_style1_table)
        sheet.write(0, 2,'Company ' , title_style_comp_left)
        sheet.write(1, 2,company_id.name, title_style1_table)
        roww = 3
        sale_lines = sale_order#.mapped("order_line")
        user_dict = {}
        row_data = roww+1
        for line in sale_lines:
            if line.state == 'sale':
                if line.user_id not in user_dict:
                    user_dict[line.user_id] = line
                else:
                    user_dict[line.user_id] +=line
        
        for user in user_dict:
            sheet.write(row_data, 0, 'Sales Person  - ' + user.name, title_style_comp)
            row_data = row_data+1
            orders = user_dict[user]
            for order in orders.sorted(key=lambda r: r.name):
                if order.expected_date:
                    sheet.write(row_data, 0, order.name+' ('+order.expected_date.strftime('%d/%m/%Y')+')', title_style_comp_1)
                else:
                    sheet.write(row_data, 0, order.name, title_style_comp_1)
                # sheet.write(row_data, 0, order.name+' ('+order.expected_date.strftime('%d/%m/%Y')+')'+' - '+order.partner_id.name+'', title_style_comp_1)
                row_data = row_data+1
                sheet.write(row_data, 0, 'Product Name',title_style1_table_head)
                column = sheet.col(0)
                column.width = 210 * 58 
                sheet.write(row_data, 1, 'Ordered Quantity',title_style1_table_head)
                column = sheet.col(1)
                column.width = 210 * 35 
                sheet.write(row_data, 2, 'Delivered Quantity',title_style1_table_head)
                column = sheet.col(2)
                column.width = 210 * 40 
                sheet.write(row_data, 3, 'Remaining Quantity',title_style1_table_head)
                column = sheet.col(3)
                column.width = 210 * 35
                row_data = row_data+1

                total = 0
                total1 = 0
                total2 = 0
                for line in order.order_line.filtered(lambda l: l.product_id):
                    total += line.product_uom_qty
                    total1 += line.qty_delivered
                    total2 += line.product_uom_qty - line.qty_delivered
                    display_name = ''
                    if line.product_id and line.product_id.default_code:
                        display_name = display_name + '['+ str(line.product_id.default_code) +']'
                    if display_name and line.product_id and line.product_id.name:
                        display_name = display_name + line.product_id.name
                    elif line.product_id and line.product_id.name:
                        display_name = line.product_id.name
                    else:
                        display_name = 'Unknown'
                    # display_name = display_name + line.product_id.name

                    sheet.write(row_data, 0, display_name , title_style1_table_data_sub)
                    sheet.write(row_data, 1, str(line.product_uom_qty)+' '+line.product_id.uom_id.name+' ', title_style1_table_data_sub_amount)
                    sheet.write(row_data, 2, str(line.qty_delivered)+' '+line.product_id.uom_id.name+' ', title_style1_table_data_sub_amount)
                    sheet.write(row_data, 3, str(round(line.product_uom_qty - line.qty_delivered, 3))+' '+line.product_id.uom_id.name+' ', title_style1_table_data_sub_amount)
                    row_data = row_data + 1
                    roww = row_data + 3

                sheet.write(row_data, 0, 'Total by Orders',title_style1_table_data)
                sheet.write(row_data, 1, str(round(total, 3)), title_style1_table_head_center)
                sheet.write(row_data, 2, str(round(total1, 3)), title_style1_table_head_center)
                sheet.write(row_data, 3, str(round(total2, 3)), title_style1_table_head_center)
                row_data = row_data+1
            sheet.write(row_data, 0,'',title_style1_table_data_sub_amount)
            row_data = row_data + 1
            roww = row_data + 3

        roww = row_data + 3
        stream = io.BytesIO()
        workbook.save(stream)
        name = 'open_orders_by_sales_person -'+ str(fields.Date.today().strftime('%d/%m/%Y'))+'.xls'
        attach_id = self.env['sale.order.user.report.output.excel'].create({
            'name':name,
            'xls_output': base64.encodebytes(stream.getvalue())
        })
        return {
            'context': self.env.context,
            # 'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.user.report.output.excel',
            'res_id':attach_id.id,
            'type': 'ir.actions.act_window',
            'target':'new'
        }
       
class SaleOrderReportExcel(models.TransientModel):
    _name = 'sale.order.user.report.output.excel'
    _description = 'Wizard to store the Excel output'

    xls_output = fields.Binary(
       string='Excel Output',
       readonly=True
    )
    name = fields.Char(
        string='File Name',
        help='Save report as .xls format',
    )