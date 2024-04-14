# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import Command, _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ["barcodes.barcode_events_mixin", "stock.move"]

    def sh_auto_serial_scanner_search_or_create_lot_serial_number(self, lot_name, product_id):
        """
            Search or Create lot number
            @param: lot_name - search record based given lot name.
            @param: product_id - Integer -  search record based given product_id.
            @return: lot object
        """
        # able to create lots, whatever the value of ` use_create_lots`.

        # Search or create lot/serial number
        lot = self.env['stock.lot'].search([('name', '=', lot_name),
                                            ('product_id', '=', product_id),
                                            ('company_id', '=', self.env.company.id)], limit=1)
        if not lot:
            lot = self.env['stock.lot'].create({'name': lot_name, 'product_id': product_id,
                                                # 'product_qty': move_line_vals['quantity'],
                                                'company_id': self.env.company.id})

        if not lot:
            raise UserError(
                _("Can't create Lots/Serial Number record for this lot/serial. % s") % (lot_name))
        return lot

    def sh_auto_serial_scanner_has_tracking_show_lots_m2o(self, barcode):

        if self.picking_code == 'incoming':
            # FOR PURCHASE
            # LOT PRODUCT
            # --------------------------------------------
            # incoming - show_lots_m2o - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                move_lines = self.move_line_ids
                lines = move_lines.filtered(lambda r: not r.lot_id)
                
                move_lines_commands = []
                if lines:
                    quantity = lines[0].quantity + 1
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id)
                    move_lines_commands = [Command.update(lines[0].id, {'quantity': quantity,'lot_name': barcode,'lot_id': lot.id})]

                else:
                    # Second Time Scan
                    lines = move_lines.filtered(lambda r: r.lot_id.name == barcode)
                    if lines:
                        quantity = lines[0].quantity + 1
                        move_lines_commands = [Command.update(lines[0].id, {'quantity': quantity})]

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands([{"lot_name": barcode, "quantity": 1}])
                        for move_line_command in move_lines_commands:
                            move_line_vals = move_line_command[2]
                            lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(barcode, self.product_id.id)
                            move_line_vals['lot_id'] = lot.id

                if move_lines_commands:
                    self.update({'move_line_ids': move_lines_commands})
                        
            # SERIAL PRODUCT
            # --------------------------------------------
            # incoming - show_lots_m2o - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                move_lines_commands = []

                # VALIDATION SERIAL NO. ALREADY EXIST.
                move_lines = self.move_line_ids
                lines = move_lines.filtered(lambda r: r.lot_id.name == barcode)
                if lines:
                    raise UserError(_("Serial Number already exist!"))
                # First Time Scan
                lines = move_lines.filtered(lambda r: not r.lot_id)
                if lines:
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(barcode, self.product_id.id)
                    move_lines_commands = [Command.update(lines[0].id, {'quantity': 1,'lot_name': barcode,'lot_id': lot.id})]

                else:
                    move_lines_commands = self._generate_serial_move_line_commands([{"lot_name": barcode, "quantity": 1}])

                    for move_line_command in move_lines_commands:
                        move_line_vals = move_line_command[2]
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(barcode, self.product_id.id)
                        move_line_vals['lot_id'] = lot.id
                if move_lines_commands:
                    self.update({'move_line_ids': move_lines_commands})
                                              

            quantity_done = 0
            for move_line in self.move_line_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.quantity, self.product_uom, round=False)
            self.move_line_ids._compute_quantity_product_uom()
            if quantity_done == self.product_uom_qty + 1:
                return {'warning': {'title': _('Alert!'), 'message': 'Becareful! Quantity exceed than initial demand!'}}

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            # --------------------------------------------
            # outgoing / internal - show_lots_m2o - lot
            # --------------------------------------------

            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([('product_id', '=', self.product_id.id),
                                          ('quantity', '>', 0),
                                          ('location_id.usage', '=', 'internal'),
                                          ('lot_id.name', '=', barcode),
                                          ('location_id', 'child_of', self.location_id.id)], limit=1)

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    raise UserError(
                        _("There are no available qty for this lot/serial.%s") % (barcode))

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id)
                # Assign lot_id in move_lines_command
                if not lot:
                    raise UserError(
                        _("Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                lines = self.move_line_ids.filtered(lambda r: not r.lot_id)

                if lines:
                    self.update({'move_line_ids': [Command.update(lines[0].id, {'quantity': lines[0].quantity + 1,'lot_id': lot.id})]})

                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        self.update({'move_line_ids': [Command.update(lines[0].id, {'quantity': lines[0].quantity + 1})]})

                    else:
                        move_lines_commands = []
                        move_line_vals = self._prepare_move_line_vals(
                            quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['quantity'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        self.update({'move_line_ids': move_lines_commands})

            # FOR SERIAL PRODUCT
            # --------------------------------------------
            # outgoing / internal - show_lots_m2o - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    raise UserError(_("Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_ids.filtered(lambda r: not r.lot_id)
                # First Time Scan
                # lines = self.move_line_ids.filtered(lambda r: r.lot_id.name == barcode)
                if lines:
                    for line in lines:
                        quantity = 1
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id)
                        self.update({'move_line_ids': [(1, line.id, {'quantity': quantity,
                                     'lot_name': barcode, 'lot_id': lot.id})]})
                        if float_compare(line.quantity, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _(
                                'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            return {"warning": {'title': _('Warning'), 'message': message}}
                        break

                else:
                    list_allocated_serial_ids = []
                    if self.move_line_ids:
                        for line in self.move_line_ids:
                            if line.lot_id:
                                list_allocated_serial_ids.append(
                                    line.lot_id.id)

                    # if need new line.
                    quant = quant_obj.search([('product_id', '=', self.product_id.id),
                                              ('quantity', '>', 0),
                                              ('location_id.usage',
                                               '=', 'internal'),
                                              ('lot_id.name', '=', barcode),
                                              ('location_id', 'child_of',
                                               self.location_id.id),
                                              ('lot_id.id', 'not in', list_allocated_serial_ids)], limit=1)

                    if not quant and not self.picking_id.picking_type_id.use_create_lots:
                        raise UserError(
                            _("There are no available qty for this lot/serial.%s") % (barcode))

                    lot = False
                    if quant and quant.lot_id:
                        lot = quant.lot_id
                    else:
                        # Create New Lot if it's allow.
                        lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                            barcode, self.product_id.id)
                    # Assign lot_id in move_lines_command
                    if not lot:
                        raise UserError(
                            _("Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                    move_lines_commands = []
                    move_line_vals = self._prepare_move_line_vals(quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['quantity'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    self.update({'move_line_ids':  move_lines_commands})

            quantity_done = 0
            for move_line in self.move_line_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.quantity, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                return {'warning': {'title': _('Alert!'), 'message': 'Becareful! Quantity exceed than initial demand!'}}
        else:
            raise UserError(
                _("Picking type is not outgoing or incoming or internal transfer."))

    def sh_auto_serial_scanner_has_tracking_show_lots_text(self, barcode):
        if self.picking_code == 'incoming':

            # FOR PURCHASE
            # LOT PRODUCT
            # --------------------------------------------
            # incoming - show_lots_text - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_name)
                if lines:
                    self.update({'move_line_ids':[Command.update(lines[0].id, {'quantity': lines[0].quantity + 1, 'lot_name': barcode})]})

                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_name == barcode)
                    if lines:
                        self.update({'move_line_ids':[Command.update(lines[0].id, {'quantity': lines[0].quantity + 1})]})

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands(
                            [{"lot_name": barcode, "quantity": 1}])
                        self.update({'move_line_ids': move_lines_commands})

            # SERIAL PRODUCT
            # --------------------------------------------
            # incoming - show_lots_text - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # lot_names = self.env['stock.lot'].generate_lot_names(barcode, False)

                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_ids.filtered(lambda r: r.lot_name == barcode)
                if lines:
                    raise UserError(_("Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_name)
                if lines:
                    self.update({'move_line_ids': [Command.update(lines[0].id, {'quantity': 1, 'lot_name': barcode})]})
                else:
                    move_lines_commands = self._generate_serial_move_line_commands([{"lot_name": barcode, "quantity": 1}])
                    self.update({'move_line_ids': move_lines_commands})

            quantity_done = 0
            for move_line in self.move_line_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.quantity, self.product_uom, round=False)

            self.move_line_ids._compute_quantity_product_uom()
            if quantity_done == self.product_uom_qty + 1:
                return {'warning': {'title': _('Alert!'), 'message': 'Becareful! Quantity exceed than initial demand!'}}

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            # --------------------------------------------
            # outgoing / internal  - show_lots_text - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([('product_id', '=', self.product_id.id),
                                          ('quantity', '>', 0),
                                          ('location_id.usage', '=', 'internal'),
                                          ('lot_id.name', '=', barcode),
                                          ('location_id', 'child_of', self.location_id.id)], limit=1)

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    raise UserError(
                        _("There are no available qty for this lot/serial.%s") % (barcode))

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id)
                # Assign lot_id in move_lines_command
                if not lot:
                    raise UserError(
                        _("Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                lines = self.move_line_ids.filtered(lambda r: not r.lot_id)
                if lines:
                    self.update({'move_line_ids':[Command.update(lines[0].id, {'quantity': lines[0].quantity + 1, 'lot_id': quant.lot_id.id})]})
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        self.update({'move_line_ids':[Command.update(lines[0].id, {'quantity':  lines[0].quantity + 1})]})
                    else:
                        move_lines_commands = []
                        lot = quant.lot_id
                        move_line_vals = self._prepare_move_line_vals(quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['quantity'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        self.update({'move_line_ids': move_lines_commands})

            # FOR SERIAL PRODUCT
            # ----------------------------------------------
            # outgoing / internal  - show_lots_text - serial
            # ----------------------------------------------
            if self.product_id.tracking == 'serial':
                list_allocated_serial_ids = []
                if self.move_line_ids:
                    for line in self.move_line_ids:
                        if line.lot_id:
                            list_allocated_serial_ids.append(line.lot_id.id)

                # if need new line.
                quant = quant_obj.search([('product_id', '=', self.product_id.id),
                                          ('quantity', '>', 0),
                                          ('location_id.usage', '=', 'internal'),
                                          ('lot_id.name', '=', barcode),
                                          ('location_id', 'child_of',
                                           self.location_id.id),
                                          ('lot_id.id', 'not in', list_allocated_serial_ids)], limit=1)

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    raise UserError(_("There are no available qty for this lot/serial.%s") % (barcode))

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_auto_serial_scanner_search_or_create_lot_serial_number(
                        barcode, self.product_id.id)
                # Assign lot_id in move_lines_command
                if not lot:
                    raise UserError(_("Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                # First Time Scan
                lines = self.move_line_ids.filtered(lambda r: r.lot_id.name == barcode)
                if lines:
                    raise UserError(_("Serial Number already exist!"))
                # First Time Scan
                lines = self.move_line_ids.filtered(lambda r: not r.lot_id)

                if lines:
                    for line in lines:
                        self.update({'move_line_ids': [(1, line.id, {'quantity': 1, 'lot_name': barcode, 'lot_id': lot.id})]})
                        if float_compare(line.quantity, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _('You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name

                            return {"warning", {'title': _('Warning'), 'message': message}}
                        break
                else:
                    move_lines_commands = []
                    move_line_vals = self._prepare_move_line_vals(quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['quantity'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    self.update({'move_line_ids':  move_lines_commands})

            quantity_done = 0
            for move_line in self.move_line_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(move_line.quantity, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                return {'warning': {'title': _('Alert!'), 'message': 'Becareful! Quantity exceed than initial demand!'}}
        else:
            raise UserError(_("Picking type is not outgoing or incoming or internal transfer."))

    def sh_auto_serial_scanner_no_tracking(self, barcode):
        move_lines = False

        move_lines = self.move_line_ids

        if move_lines:
            for line in move_lines:
                if self.product_id.barcode == barcode:
                    quantity = line.quantity + 1
                    self.move_line_ids = [Command.update(line.id, {'quantity': quantity})]
                    if self.quantity_done == self.product_uom_qty + 1:
                        return {'warning': {'title': _('Alert!'), 'message': 'Becareful! Quantity exceed than initial demand!'}}
                    break
                else:
                    raise UserError(_("Scanned Internal Reference/Barcode not exist in any product"))
            self.move_line_ids._compute_quantity_product_uom()
        else:
            raise UserError(
                _("Please add all product items in line than rescan."))

    def on_barcode_scanned(self, barcode):

        show_lots_m2o = self.has_tracking != 'none' and (self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id)
        show_lots_text = self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id

        if self.picking_id.state not in ['confirmed', 'assigned']:
            selections = self.picking_id.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] ==
                         self.picking_id.state), self.picking_id.state)
            raise UserError(_("You can not scan item in %s state.") % (value))

        res = {}

        if show_lots_m2o:
            res = self.sh_auto_serial_scanner_has_tracking_show_lots_m2o(barcode)

        elif show_lots_text:
            res = self.sh_auto_serial_scanner_has_tracking_show_lots_text(barcode)
        else:
            res = self.sh_auto_serial_scanner_no_tracking(barcode)
        return res
