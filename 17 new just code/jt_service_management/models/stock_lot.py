# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta


class Partner(models.Model):
    _inherit = 'res.partner'

    supplier_warranty = fields.Integer("Supplier Warranty (month's)")
    customer_warranty = fields.Integer("Customer Warranty (month's)")
    

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            if picking.picking_type_id.code == 'incoming':
                # boe = picking.bill_of_entry
                date_start_dt = picking.scheduled_date
                name = picking.name
                supplier_warranty = picking.partner_id and picking.partner_id.supplier_warranty or 0
                
                for move in picking.move_ids_without_package:
                    for move_line in move.move_line_ids:
                        lot = move_line.lot_id
                        if lot:
                            lot.supplier_id = picking.partner_id and picking.partner_id.id or False 
                            # lot.bill_of_entry_num = boe
                            lot.shipment_date = str(date_start_dt)
                            lot.shipment_num = name
                            lot.start_date_sup_warranty = str(date_start_dt)
                            lot.end_date_sup_warranty = str(date_start_dt + relativedelta(months=int(supplier_warranty)))
                # else:
                #     if picking.is_bill_of_entry and not picking.bill_of_entry:
                #         raise UserError(_('Please Enter Bill Of Entry'))
            if picking.picking_type_id.code == 'outgoing':
                # boe = picking.bill_of_entry
                partner_id = picking.partner_id.id
                date_start_dt = picking.scheduled_date
                name = picking.name
                for move in picking.move_ids_without_package:
                    for move_line in move.move_line_ids:
                        if move_line.lot_id:
                            lot = move_line.lot_id
                            customer_warranty = lot.supplier_id and lot.supplier_id.customer_warranty or 0 
                            company_partner_id = self.env['res.company'].sudo().search([('partner_id','child_of',partner_id)])
                    
                            if not lot.partner_id:
                                lot.partner_id = partner_id

                            if lot.partner_id and not company_partner_id:
                                lot.partner_id = partner_id
                                    
                            lot.delivery_date = str(date_start_dt)
                            lot.delivery_order_num = name
                            lot.start_date_warranty = str(date_start_dt)
                            lot.end_date_warranty = str(date_start_dt + relativedelta(months=int(customer_warranty)))
        return res

        
class StockLot(models.Model):
    _inherit = 'stock.lot'

    warranty_periods = fields.Selection([('under_warranty','Under Warranty'),
                                          ('warranty_expired','Warranty Expired'),
                                          ('warranty_extended','Warranty Extended')],readonly=True)
    partner_id = fields.Many2one('res.partner','Customer', tracking=True)
    start_date_warranty = fields.Date('Warranty Start Date', tracking=True)
    end_date_warranty = fields.Date('Warranty End Date', tracking=True)
    start_date_sup_warranty = fields.Date('Supplier Warranty Start Date', tracking=True)
    end_date_sup_warranty = fields.Date('Supplier Warranty End Date', tracking=True)
    sup_warranty_periods = fields.Selection([('under_warranty', 'Under Warranty'),
                                          ('warranty_expired', 'Warranty Expired'),
                                          ('warranty_extended', 'Warranty Extended')], readonly=True)
    delivery_date = fields.Date('Delivery Date', tracking=True)
    supplier_id = fields.Many2one('res.partner','Supplier')
    shipment_date = fields.Date('Receipt Date', tracking=True)
    shipment_num = fields.Char('Receipt No', tracking=True)
