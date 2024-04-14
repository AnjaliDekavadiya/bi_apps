# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class PickingIncomingOutgoing(models.TransientModel):
    _name = "picking.incoming.outgoing"
    _description = 'Picking Incoming Outgoing'

    files = fields.Binary(
        string="Import Excel File",
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id.id,
    )

    custom_picking_type_id = fields.Many2one(
        'stock.picking.type', 
        'Operation Type',
        required=True,
    )

    is_done = fields.Selection(selection=[
        ('draft','Draft'),
        ('confirmed','Confirmed')],
        default='draft',
        string='State', 
        required=True,
    )

    datas_fname = fields.Char(
        string = 'Import File Name'
    )

    custom_location_id = fields.Many2one(
        'stock.location',
        "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        required=True,
    )
    custom_location_dest_id = fields.Many2one(
        'stock.location', 
        "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        required=True,
    )

    import_product_variants_by = fields.Selection(selection=[
        ('name','Name'),
        ('code','Code'),
        ('barcode','Barcode')],
        string='Import Product Using',
        default='name',
        required=True,
    )

#    @api.multi #odoo13
    def picking_incoming_outgoing_with_excel(self):
        try:
            #workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        stock_picking =[]
        list_partner = []
        vals = {}
        excel_dict={}
        partner_dict={}
        partner=self.env['res.partner']
        owner=self.env['res.partner']
        operationobj=self.env['stock.picking.type']
        product_id=self.env['product.product']
#        unitObj=self.env['uom.uom']
        #lot = self.env['stock.production.lot']
        lot = self.env['stock.lot']
        row = 1

        while(row < number_of_rows):
            Number = sheet.cell(row,0).value
            partner_id = sheet.cell(row,1).value

            if partner_id in partner_dict:
                partner_id=partner_dict[partner_id]
                list_partner.append(partner_id)
            if Number in partner_dict:
                partner_id = partner_dict.get(Number)
            
            if partner_id:
                partner_dict.update({Number:partner_id})
                list_partner.append(partner_id)
                partner_id=partner.search([('name', '=', partner_id)], limit=1)

            document = sheet.cell(row,2).value

            owner_id=sheet.cell(row,3).value
            if owner_id:
                ownerObj=owner.search([('name', '=', owner_id)], limit=1)

            shipping_policy=sheet.cell(row,4).value

            if Number:
                vals = { 
                    'partner_id':partner_id.id,
                    'origin':document,
                    'owner_id':ownerObj.id,
                    'company_id':self.company_id.id,
                    'picking_type_id':self.custom_picking_type_id.id,
                    'location_id':self.custom_location_id.id,
                    'location_dest_id':self.custom_location_dest_id.id,
                }
                picking_id =self.env['stock.picking'].create(vals)
                excel_dict.update({Number:picking_id})
                stock_picking.append(picking_id.id)
                number_row = row
            else:
                Number=sheet.cell(number_row,0).value
                picking_id=excel_dict[Number]

            product_line_id=sheet.cell(row,5).value
            if self.import_product_variants_by == 'name':
                product_lineId=product_id.search([('name', '=', product_line_id),('company_id','=',self.company_id.id)], limit=1)
                if not product_lineId:
                    product_lineId = product_id.search([('name', '=', product_line_id)], limit=1)
            elif self.import_product_variants_by == 'code':
                product_lineId=product_id.search([('default_code', '=', str(product_line_id)),('company_id','=',self.company_id.id)], limit=1)
                if not product_lineId:
                    product_lineId = product_id.search([('default_code', '=', str(product_line_id))], limit=1)

            elif self.import_product_variants_by == 'barcode':
                product_lineId=product_id.search([('barcode', '=', str(product_line_id)),('company_id','=',self.company_id.id)], limit=1)
                if not product_lineId:
                    product_lineId = product_id.search([('barcode', '=', str(product_line_id))], limit=1)

            if not product_lineId:
                raise ValidationError(
                    'Product %s not found in the system  : row number %s '%(
                        sheet.cell(row,5).value,row+1
                    )
                )
          
            description=sheet.cell(row,6).value

            product_uom_qty = sheet.cell(row,7).value
            if not product_uom_qty:
                raise ValidationError('Quantity should not be empty at row %s in excel file.'%(row+1))

            line_vals = { 
                'product_id':product_lineId.id,
                'product_uom_qty':product_uom_qty,
                'picking_id':picking_id.id, 
                'name':description,
                'location_id':self.custom_location_id.id,
                'location_dest_id':self.custom_location_dest_id.id,  
            }

            move_id = self.env['stock.move'].new(line_vals)
            #move_id.onchange_product_id()
            move_id._onchange_product_id()
            values = move_id._convert_to_write({
               name: move_id[name] for name in move_id._cache
            })
            stock_move_id =self.env['stock.move'].create(values)
            tracking =sheet.cell(row,8).value

            if tracking == 'lot':
                lot_id=sheet.cell(row,9).value
                if lot_id:
                    lot_ID=lot.search([('name', '=', lot_id),
                                    ('product_id','=',product_lineId.id),
                    ])
                stock_move_line = self.env['stock.move.line']
                move_line= { 
                    'lot_id':lot_ID.id,
                    'move_id':stock_move_id.id,
                    'picking_id':picking_id.id,
                    'product_id':product_lineId.id,
                    'tracking':tracking,
                    'qty_done': product_uom_qty,
                    'product_uom_id': stock_move_id.product_uom.id,
                    'location_id':self.custom_location_id.id,
                    'location_dest_id':self.custom_location_dest_id.id,  
                }
                moves_id = stock_move_line.with_context(show_lots_m2o = True).create(move_line)
                stock_move_id.write({'move_line_ids' : [(4,moves_id.id)]})
            
            elif tracking == 'serial':
                serial_lot = []
                serial=sheet.cell(row,10).value
                if serial: 
                    serial_number = serial.split(',')
                    for lot_serial in serial_number:
                        serial_ID=lot.search([('name', '=', lot_serial),
                                              ('product_id','=',product_lineId.id),
                        ])
                        serial_lot.append(serial_ID.id)

                for serial_no in serial_lot:
                    stock_move_line = self.env['stock.move.line']
                    move_line= { 
                        'lot_id':serial_no,
                        'move_id':stock_move_id.id,
                        'picking_id':picking_id.id,
                        'product_id':product_lineId.id,
                        'qty_done': product_uom_qty,
                        'product_uom_id': stock_move_id.product_uom.id,
                        'location_id':self.custom_location_id.id,
                        'location_dest_id':self.custom_location_dest_id.id,  
                    }
                    moves_id = stock_move_line.with_context(show_lots_m2o = True).create(move_line)
                    stock_move_id.write({'move_line_ids' : [(4,moves_id.id)]})
            if self.is_done == 'confirmed':        
                picking_id.action_confirm()
                picking_id.action_assign()
            row = row + 1
        action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action['domain'] = [('id', 'in', stock_picking)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
