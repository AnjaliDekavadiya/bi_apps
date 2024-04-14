# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
import json
from odoo.tools import date_utils, float_round
from odoo.exceptions import ValidationError, RedirectWarning
from io import BytesIO
import xlsxwriter
from datetime import datetime
from odoo.osv import expression
import calendar

class AccountReport(models.Model):
    _inherit = 'account.report'
    
    def export_kardex(self, options):
        return {
            'type': 'ir_actions_account_report_download',
            'data': {
                 'options': json.dumps(options, default=date_utils.json_default),
                 'file_generator': 'create_file_kardex_format',
             }
        }
        
    def not_implemented_yet(self, report_name):
        raise ValidationError(_('The report %s is not implemented yet. Check the module page for updates.') %report_name)

    def create_file_kardex_format(self, options):
        '''Función para crear archivo txt'''
        self.ensure_one()
        file_content = ''
        if options['format'] == '1':
            file_content = self._create_file_kardex_xlsx(options)
            file_name = options.get('report_name') + '.xlsx'
            file_type = 'xlsx'
        return {
            'file_name': file_name,
            'file_content': file_content,
            'file_type': file_type,
        }
    
    def _create_file_kardex_xlsx(self, options):
        # Filtro por reporte dependiendo del nombre
        report_code = options.get('report_code')
        if report_code == 'kardex': # Kardex Sunat formato 13.1
            data = self._get_xlsx_kardex(options)
        if not data:
            raise ValidationError(_('There is no data in report %s') % options['report_name'])
        return data

    def _get_serie(self, name):
        '''Función para obtener la serie del documento que fue previamente
        registrado con el formato establecido por SUNAT'''
        if not name:
            return ''
        serie = name.split('-')
        if len(serie) == 2:
            serie = serie[0].split(' ')
            serie = serie[1] if len(serie) == 2 else serie[0]
        else:
            serie = ''
        return serie

    def _get_number(self, name):
        '''Función para obtener el numero del documento que fue previamente
        registrado con el formato establecido por SUNAT'''
        if not name:
            return ''
        number = name.split('-')
        if len(number) == 2:
            number = number[1]
        else:
            number = name.split(' ')
            number = number[1] if len(number) == 2 else number[0]
        return number

    ##############################
    # FUNCIONES DE REPORTES XLSX #
    ##############################

    def _get_xlsx_kardex(self, options):
        '''Kardex Sunat formato 13.1'''
        self.name = '001'
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        products = self.env['product.product'].search([('id','in',options['product_ids'])])
        row = 1
        for product in products:
            row = self._header(options, workbook, worksheet, product, row)
            if product.categ_id.property_valuation == 'real_time':
                row = self._data_real_time(options, workbook, worksheet, product, row)
            else:
                row = self._data_manual(options, workbook, worksheet, product, row)
            row += 2
        # Fin del reporte
        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        return generated_file
        
    def _header(self, options, workbook, worksheet, product, row):
        # obteniendo precision decimal
        digits = self.env['decimal.precision'].precision_get('Product Price')
        _digits = ''.zfill(digits)
        qty_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        _qty_digits = ''.zfill(qty_digits)

        format_title = workbook.add_format({'bold': 1, 'text_wrap': 1, 'font_size': 15, 'align': 'center',
                                         'valign': 'vcenter'})
        format_center_bold = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'center', 'valign': 'vcenter'})
        format_lef_bold = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'left', 'valign': 'vcenter'})
        format_left = workbook.add_format({'text_wrap': 1, 'align': 'left', 'valign': 'vcenter'})
        format_A7 = workbook.add_format({'bold': 1, 'text_wrap': 1, 'font_size': 15, 'align': 'left',
                                         'valign': 'vcenter'})
        merge_format_vc = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'center', 'valign': 'vcenter',
                                               'border': 1, 'bg_color': '#d1d1d1'})
        format_line_qty = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_qty_digits}'})
        format_line_num = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_digits}'})
        format_line_tot = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.00'})
        format_line = workbook.add_format({'valign': 'vcenter'})
        format_top_border = workbook.add_format({'top': 1, 'valign': 'vcenter'})
        style_bold_qty = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'num_format': f'#,##0.{_qty_digits}'})
        style_bold_tot = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'num_format': f'#,##0.00'})
        style_bold = workbook.add_format({'bold': 1, 'valign': 'vcenter'})

        # Ancho de Columna, Alto de Filas, Zoom
        worksheet.set_column('A:A', 25, None)
        worksheet.set_column('B:B', 13, None)
        worksheet.set_column('C:C', 15, None)
        worksheet.set_column('D:D', 15, None)
        worksheet.set_column('E:E', 26, None)
        # ENTRADAS
        worksheet.set_column('F:F', 15, None)
        worksheet.set_column('G:G', 15, None)
        worksheet.set_column('H:H', 15, None)
        # SALIDAS
        worksheet.set_column('I:I', 15, None)
        worksheet.set_column('J:J', 15, None)
        worksheet.set_column('K:K', 15, None)
        # SALDO FINAL
        worksheet.set_column('L:L', 15, None)
        worksheet.set_column('M:M', 15, None)
        worksheet.set_column('N:N', 15, None)
        worksheet.set_column('Q:Q', 12, None)
        # if self.debug:
        #     worksheet.set_column('R:R', 20, None)
        worksheet.set_row(row, 50)
        worksheet.set_zoom(80)
        worksheet.hide_gridlines(2)

        name_month = calendar.month_name[datetime.strptime(options['date']['date_from'], '%Y-%m-%d').month]
        periodo = name_month + ' ' + options['date']['date_from'][:4]

        worksheet.merge_range('A' + str(row+1) + ':N' + str(row+1), 'FORMATO 13.1: "REGISTRO DE INVENTARIO PERMANENTE VALORIZADO - \n' +
                              'DETALLE DEL INVENTARIO VALORIZADO"', format_title)

        row += 4

        # Cabeceras
        # Periodo
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Periodo: ' + periodo, format_lef_bold)
        row += 1

        # RUC
        if not self.env.company.partner_id.vat:
            raise RedirectWarning(
                _('Please insert company vat number'),
                self.env.ref('base_setup.action_general_configuration').id,
                _("Go to the configuration panel"),
            )
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'RUC: ' + self.env.company.partner_id.vat,
                              format_lef_bold)
        row += 1

        # Compañía
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':I' + str(row), self.env.company.partner_id.name, format_A7)
        row += 1

        # Establecimiento
        worksheet.set_row(row, 35)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Establecimiento: ', format_lef_bold)
        worksheet.merge_range('C' + str(row) + ':I' + str(row), self.env.company.partner_id.name, format_left)
        row += 1

        # Cod. Existencia
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Cod. Existencia: ', format_lef_bold)
        worksheet.merge_range('C' + str(row) + ':E' + str(row),
                              product.default_code if product.default_code else '',
                              format_left)
        row += 1

        # Tipo (Tabla 5)
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Tipo (Tabla 5): ', format_lef_bold)
        worksheet.merge_range('C' + str(row) + ':E' + str(row),
                               product.existence_type_id.code + ' - ' + product.existence_type_id.name if product.existence_type_id else '',
                               format_left)
        row += 1

        # Descripción
        worksheet.set_row(row, 40)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Descripción: ', format_lef_bold)
        worksheet.merge_range('C' + str(row) + ':E' + str(row), product.name, format_left)
        row += 1

        # Unidad de Medida
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Cod. Unidad de Medida: ',
                              format_lef_bold)
        # TODO sunat code
        product_uom = '' #product.uom_id.sunat_code or ''
        if product_uom:
            product_uom += ' '
        product_uom = product_uom + product.uom_id.name or ''
        worksheet.merge_range('C' + str(row) + ':E' + str(row), product_uom, format_left)
        row += 1

        # Método de Valuación
        worksheet.set_row(row, 25)
        worksheet.merge_range('A' + str(row) + ':B' + str(row), 'Método de Valuación: ',
                              format_lef_bold)
        # worksheet.merge_range('C' + str(row) + ':E' + str(row), product.categ_id.property_cost_method, format_left)
        method = dict(product.categ_id._fields['property_cost_method']._description_selection(self.env)).get(product.categ_id.property_cost_method)
        worksheet.merge_range('C' + str(row) + ':E' + str(row), method, format_left)
        row += 1
        # Espacio despues de la info
        worksheet.set_row(row, 40)
        row += 1

        worksheet.set_row(row, 40)  # 1.ª fila del encabezado
        worksheet.merge_range('A' + str(row) + ':D' + str(row),
                              'DOCUMENTO DE TRASLADO, COMPROBANTE DE PAGO, DOCUMENTO INTERNO O SIMILAR',
                              merge_format_vc)
        worksheet.merge_range('E' + str(row) + ':E' + str(row + 1),
                              'TIPO DE OPERACIÓN (TABLA 12)', merge_format_vc)
        # Entradas
        worksheet.merge_range('F' + str(row) + ':H' + str(row), 'ENTRADAS', merge_format_vc)
        
        # Salidas
        worksheet.merge_range('I' + str(row) + ':K' + str(row), 'SALIDAS', merge_format_vc)
        
        # Saldo Final
        worksheet.merge_range('L' + str(row) + ':N' + str(row), 'SALDO FINAL', merge_format_vc)
        
        # # Ubicaciones
        worksheet.merge_range('O' + str(row) + ':P' + str(row), 'UBICACIONES', merge_format_vc)
        
        row += 1

        worksheet.set_row(row, 30)
        worksheet.write_string('A' + str(row), 'FECHA', merge_format_vc)
        worksheet.write_string('B' + str(row), 'TIPO (TABLA 10)', merge_format_vc)
        worksheet.write_string('C' + str(row), 'SERIE', merge_format_vc)
        worksheet.write_string('D' + str(row), 'NÚMERO', merge_format_vc)

        # Entradas
        worksheet.write_string('F' + str(row), 'CANTIDAD', merge_format_vc)
        worksheet.write_string('G' + str(row), 'COSTO UNITARIO', merge_format_vc)
        worksheet.write_string('H' + str(row), 'COSTO TOTAL', merge_format_vc)

        # Salidas
        worksheet.write_string('I' + str(row), 'CANTIDAD', merge_format_vc)
        worksheet.write_string('J' + str(row), 'COSTO UNITARIO', merge_format_vc)
        worksheet.write_string('K' + str(row), 'COSTO TOTAL', merge_format_vc)

        # Saldo Final
        worksheet.write_string('L' + str(row), 'CANTIDAD', merge_format_vc)
        worksheet.write_string('M' + str(row), 'COSTO UNITARIO', merge_format_vc)
        worksheet.write_string('N' + str(row), 'COSTO TOTAL', merge_format_vc)

        # # Ubicaciones
        worksheet.write_string('O' + str(row), 'ORIGEN', merge_format_vc)
        worksheet.write_string('P' + str(row), 'DESTINO', merge_format_vc)
        
        return row + 1

    def _data_real_time(self, options, workbook, worksheet, product, row):
        debug = options['debug']
        # obteniendo precision decimal
        digits = self.env['decimal.precision'].precision_get('Product Price')
        _digits = ''.zfill(digits)
        qty_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        _qty_digits = ''.zfill(qty_digits)
        format_line_qty = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_qty_digits}'})
        format_line_num = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_digits}'})
        format_txt = workbook.add_format({'valign': 'vcenter'})
        format_date = workbook.add_format({'valign': 'vcenter'})
        format_total = workbook.add_format({'valign': 'vcenter', 'bold': 1})
        format_total_num = workbook.add_format({'valign': 'vcenter', 'bold': 1, 'num_format': f'#,##0.{_digits}'})
        format_top_border = workbook.add_format({'top': 1, 'valign': 'vcenter'})
        row, total_qty, total_cost = self._get_kardex_initial_balance_real_time(options, workbook, worksheet, product, row)
        pickings = self.env['stock.picking'].search([('date_done','>=', options['date']['date_from']),('date_done','<=', options['date']['date_to'])])
        moves = self.env['stock.move'].search([('picking_id','in', pickings.ids),('product_id','=', product.id)]).sorted('date')
        final_in_cost = final_in_qty = final_out_cost = final_out_qty = cost = expense = 0
        for move in moves:
            svls = self.env['stock.valuation.layer'].read_group([('stock_move_id','=', move.id),('stock_valuation_layer_id','=', False)], ['quantity:sum','unit_cost:sum','value:sum','stock_move_id'], ['stock_move_id'])
            svl = svls[0]
            if svl:
                worksheet.write_string('A' + str(row), fields.Datetime.to_string(move.picking_id.date_done), format_date)
                worksheet.write_string('B' + str(row), move.picking_id.l10n_latam_document_type_id.code or '', format_txt)
                worksheet.write_string('C' + str(row), move.picking_id.serie or '', format_txt)
                worksheet.write_string('D' + str(row), move.picking_id.number or '', format_txt)
                worksheet.write_string('E' + str(row), (move.picking_id.type_operation_id.code or '') + ' - ' + (move.picking_id.type_operation_id.name or ''), format_txt)
                # for svl in svls:
                # Buscamos si hay costos en destino para este move y si tiene
                # lo agregamos al valor total
                slcs = self.env['stock.landed.cost'].search([('picking_ids','in', move.picking_id.id)])
                # if slcs and not debug:
                    # for l in slcs.account_move_id.line_ids:
                    #     print(l.account_id.account_type, l.product_id, l.balance, l.account_id.account_type == 'asset_current', l.product_id == move.product_id)
                    #     print(slcs.account_move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_current' and l.product_id == move.product_id).mapped('balance'))
                    #     print(slcs.account_move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_current' and l.product_id == move.product_id))
                    # svl['value'] += sum(slcs.account_move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_current' and l.product_id == move.product_id).mapped('balance'))
                if move.picking_id.picking_type_code == 'incoming':
                    if slcs and not debug:
                        # Agregamos los costos en destino y si hay gastos de mercadería q fue vendida antes lo restamos
                        cost = sum(slcs.valuation_adjustment_lines.filtered(lambda l: l.product_id == move.product_id).mapped('additional_landed_cost'))
                        # sum(slcs.account_move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_current' and l.product_id == move.product_id).mapped('balance'))
                        expense = sum(slcs.account_move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'expense_direct_cost' and l.product_id == move.product_id).mapped('balance'))
                        svl['value'] += cost #- expense
                    if move.origin_returned_move_id:
                        worksheet.write_number('F' + str(row), svl['quantity'], format_line_qty)
                        worksheet.write_number('G' + str(row), svl['value'] / svl['quantity'], format_line_num)
                        worksheet.write_number('H' + str(row), svl['value'], format_line_num)
                        final_in_qty -= svl['quantity']
                        final_in_cost -= svl['value']
                    else:
                        worksheet.write_number('F' + str(row), svl['quantity'], format_line_qty)
                        worksheet.write_number('G' + str(row), svl['value'] / svl['quantity'], format_line_num)
                        worksheet.write_number('H' + str(row), svl['value'], format_line_num)
                        final_in_qty += svl['quantity']                        
                        final_in_cost += svl['value']
                else:
                    if move.origin_returned_move_id:
                        worksheet.write_number('I' + str(row), abs(svl['quantity']), format_line_qty)
                        worksheet.write_number('J' + str(row), svl['value'] / svl['quantity'], format_line_num)
                        worksheet.write_number('K' + str(row), abs(svl['value']), format_line_num)
                        final_out_qty -= abs(svl['quantity'])
                        final_out_cost -= abs(svl['value'])
                    else:
                        worksheet.write_number('I' + str(row), abs(svl['quantity']), format_line_qty)
                        worksheet.write_number('J' + str(row), svl['value'] / svl['quantity'], format_line_num)
                        worksheet.write_number('K' + str(row), abs(svl['value']), format_line_num)
                        final_out_qty -= svl['quantity']
                        final_out_cost -= svl['value']
                total_qty += svl['quantity']
                total_cost += svl['value']
                worksheet.write_number('L' + str(row), total_qty, format_line_qty)
                worksheet.write_number('M' + str(row), 0 if total_qty == 0 else total_cost / total_qty, format_line_num)
                worksheet.write_number('N' + str(row), total_cost, format_line_num)
                worksheet.write_string('O' + str(row), move.picking_id.location_id.complete_name, format_txt)
                worksheet.write_string('P' + str(row), move.picking_id.location_dest_id.complete_name, format_txt)
                row += 1
                if expense:
                    # slc_value = sum(slcs.valuation_adjustment_lines.filtered(lambda l: l.product_id == move.product_id).mapped('additional_landed_cost'))
                    # worksheet.write_string('A' + str(row), fields.Datetime.to_string(slc.account_move_id.write_date), format_date)
                    worksheet.write_string('E' + str(row), _('Already out'), format_txt)
                    worksheet.write_number('K' + str(row), expense, format_line_num)
                    final_out_cost += expense
                    total_cost -= expense
                    worksheet.write_number('L' + str(row), total_qty, format_line_qty)
                    worksheet.write_number('M' + str(row), 0 if total_qty == 0 else total_cost / total_qty, format_line_num)
                    worksheet.write_number('N' + str(row), total_cost, format_line_num)
                    # last_price = 0 if total_qty == 0 else total_cost / total_qty
                    row += 1
                    expense = 0
                if slcs and debug:
                    for slc in slcs:
                        slc_value = sum(slcs.valuation_adjustment_lines.filtered(lambda l: l.product_id == move.product_id).mapped('additional_landed_cost'))
                        worksheet.write_string('A' + str(row), fields.Datetime.to_string(slc.account_move_id.write_date), format_date)
                        worksheet.write_string('D' + str(row), slc.name or '', format_txt)
                        worksheet.write_number('H' + str(row), slc_value, format_line_num)
                        final_in_cost += slc_value
                        total_cost += slc_value
                        worksheet.write_number('L' + str(row), total_qty, format_line_qty)
                        worksheet.write_number('M' + str(row), 0 if total_qty == 0 else total_cost / total_qty, format_line_num)
                        worksheet.write_number('N' + str(row), total_cost, format_line_num)
                        # last_price = 0 if total_qty == 0 else total_cost / total_qty
                        row += 1
                        expense += sum(slc.account_move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'expense_direct_cost' and l.product_id == move.product_id).mapped('balance'))
                        if expense:
                            # slc_value = sum(slcs.valuation_adjustment_lines.filtered(lambda l: l.product_id == move.product_id).mapped('additional_landed_cost'))
                            # worksheet.write_string('A' + str(row), fields.Datetime.to_string(slc.account_move_id.write_date), format_date)
                            worksheet.write_string('E' + str(row), _('Already out'), format_txt)
                            worksheet.write_number('K' + str(row), expense, format_line_num)
                            final_out_cost += expense
                            total_cost -= expense
                            worksheet.write_number('L' + str(row), total_qty, format_line_qty)
                            worksheet.write_number('M' + str(row), 0 if total_qty == 0 else total_cost / total_qty, format_line_num)
                            worksheet.write_number('N' + str(row), total_cost, format_line_num)
                            # last_price = 0 if total_qty == 0 else total_cost / total_qty
                            row += 1
                            expense = 0
        worksheet.merge_range('A' + str(row) + ':' + 'N' + str(row), '', format_top_border)
        row += 1
        worksheet.write_string('E' + str(row), 'Totales', format_total)
        worksheet.write_number('F' + str(row), final_in_qty, format_total_num)
        worksheet.write_number('I' + str(row), final_out_qty, format_total_num)
        worksheet.write_number('H' + str(row), final_in_cost, format_total_num)
        worksheet.write_number('K' + str(row), final_out_cost, format_total_num)
        return row

    def _get_kardex_initial_balance_real_time(self, options, workbook, worksheet, product, row):
        # obteniendo precision decimal
        digits = self.env['decimal.precision'].precision_get('Product Price')
        _digits = ''.zfill(digits)
        qty_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        _qty_digits = ''.zfill(qty_digits)
        format_line_qty = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_qty_digits}'})
        format_line_num = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_digits}'})
        format_initial = workbook.add_format({'valign': 'vcenter', 'color': 'blue'})
        total_qty = total_cost = 0
        pickings = self.env['stock.picking'].search([('date_done','<', options['date']['date_from'])])
        moves = self.env['stock.move'].search([('picking_id','in', pickings.ids),('product_id','=', product.id)])
        svls = self.env['stock.valuation.layer'].read_group([('stock_move_id','in', moves.ids)], ['quantity:sum','unit_cost:sum','value:sum','product_id'], ['product_id'])
        worksheet.write_string('K' + str(row), 'Saldo Inicial', format_initial)
        if svls:
            for svl in svls:
                worksheet.write_number('L' + str(row), svl['quantity'], format_line_qty)
                worksheet.write_number('M' + str(row), svl['value'] / svl['quantity'], format_line_num)
                worksheet.write_number('N' + str(row), svl['value'], format_line_num)
                total_qty += svl['quantity']
                total_cost += svl['value']
        else:
            worksheet.write_number('L' + str(row), 0, format_line_qty)
            worksheet.write_number('M' + str(row), 0, format_line_num)
            worksheet.write_number('N' + str(row), 0, format_line_num)
            total_qty = 0
            total_cost = 0
        row += 1
        return row, total_qty, total_cost
    
    def _data_manual(self, options, workbook, worksheet, product, row):
        # obteniendo precision decimal
        digits = self.env['decimal.precision'].precision_get('Product Price')
        _digits = ''.zfill(digits)
        qty_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        _qty_digits = ''.zfill(qty_digits)
        format_line_qty = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_qty_digits}'})
        format_line_num = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_digits}'})
        format_txt = workbook.add_format({'valign': 'vcenter'})
        format_date = workbook.add_format({'valign': 'vcenter'})
        format_total = workbook.add_format({'valign': 'vcenter', 'bold': 1})
        format_total_num = workbook.add_format({'valign': 'vcenter', 'bold': 1, 'num_format': f'#,##0.{_digits}'})
        format_top_border = workbook.add_format({'top': 1, 'valign': 'vcenter'})
        row, total_qty, total_cost = self._get_kardex_initial_balance_manual(options, workbook, worksheet, product, row)
        pickings = self.env['stock.picking'].search([('date_done','>=', options['date']['date_from']),('date_done','<=', options['date']['date_to'])])
        moves = self.env['stock.move'].search([('picking_id','in', pickings.ids),('product_id','=', product.id)]).sorted('date')
        final_in_cost = final_in_qty = final_out_cost = final_out_qty = 0
        for move in moves:
            svls = self.env['stock.valuation.layer'].read_group([('stock_move_id','=', move.id)], ['quantity:sum','unit_cost:sum','value:sum','stock_move_id'], ['stock_move_id'])
            if svls:
                worksheet.write_string('A' + str(row), fields.Datetime.to_string(move.picking_id.date_done), format_date)
                worksheet.write_string('B' + str(row), move.picking_id.l10n_latam_document_type_id.code, format_txt)
                worksheet.write_string('C' + str(row), move.picking_id.serie or '', format_txt)
                worksheet.write_string('D' + str(row), move.picking_id.number or '', format_txt)
                worksheet.write_string('E' + str(row), move.picking_id.type_operation_id.code + ' - ' + move.picking_id.type_operation_id.name, format_txt)
                for svl in svls:
                    if move.picking_id.picking_type_code == 'incoming':
                        if move.origin_returned_move_id:
                            worksheet.write_number('I' + str(row), -svl['quantity'], format_line_qty)
                            worksheet.write_number('J' + str(row), svl['value'] / svl['quantity'], format_line_num)
                            worksheet.write_number('K' + str(row), -svl['value'], format_line_num)
                            final_out_cost -= svl['value']
                            final_out_qty -= svl['quantity']
                        else:
                            worksheet.write_number('F' + str(row), svl['quantity'], format_line_qty)
                            worksheet.write_number('G' + str(row), svl['value'] / svl['quantity'], format_line_num)
                            worksheet.write_number('H' + str(row), svl['value'], format_line_num)
                            final_in_cost += svl['value']
                            final_in_qty += svl['quantity']
                    else:
                        if move.origin_returned_move_id:
                            worksheet.write_number('F' + str(row), svl['quantity'], format_line_qty)
                            worksheet.write_number('G' + str(row), svl['value'] / svl['quantity'], format_line_num)
                            worksheet.write_number('H' + str(row), svl['value'], format_line_num)
                            final_in_cost -= abs(svl['value'])
                            final_in_qty -= abs(svl['quantity'])
                        else:
                            worksheet.write_number('I' + str(row), abs(svl['quantity']), format_line_qty)
                            worksheet.write_number('J' + str(row), svl['value'] / svl['quantity'], format_line_num)
                            worksheet.write_number('K' + str(row), abs(svl['value']), format_line_num)
                            final_out_cost += abs(svl['value'])
                            final_out_qty += abs(svl['quantity'])
                    total_qty += svl['quantity']
                    total_cost += svl['value']
                worksheet.write_number('L' + str(row), total_qty, format_line_qty)
                worksheet.write_number('M' + str(row), 0 if total_qty == 0 else total_cost / total_qty, format_line_num)
                worksheet.write_number('N' + str(row), total_cost, format_line_num)
                row += 1
        worksheet.merge_range('A' + str(row) + ':' + 'N' + str(row), '', format_top_border)
        row += 1
        worksheet.write_string('E' + str(row), 'Totales', format_total)
        worksheet.write_number('F' + str(row), final_in_qty, format_total_num)
        worksheet.write_number('I' + str(row), final_out_qty, format_total_num)
        worksheet.write_number('H' + str(row), final_in_cost, format_total_num)
        worksheet.write_number('K' + str(row), final_out_cost, format_total_num)
        return row

    def _get_kardex_initial_balance_manual(self, options, workbook, worksheet, product, row):
        # obteniendo precision decimal
        digits = self.env['decimal.precision'].precision_get('Product Price')
        _digits = ''.zfill(digits)
        qty_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        _qty_digits = ''.zfill(qty_digits)
        format_line_qty = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_qty_digits}'})
        format_line_num = workbook.add_format({'valign': 'vcenter', 'num_format': f'#,##0.{_digits}'})
        format_initial = workbook.add_format({'valign': 'vcenter', 'color': 'blue'})
        total_qty = total_cost = 0
        pickings = self.env['stock.picking'].search([('date_done','<', options['date']['date_from'])])
        moves = self.env['stock.move'].search([('picking_id','in', pickings.ids),('product_id','=', product.id)])
        svls = self.env['stock.valuation.layer'].read_group([('stock_move_id','in', moves.ids)], ['quantity:sum','unit_cost:sum','value:sum','product_id'], ['product_id'])
        worksheet.write_string('K' + str(row), 'Saldo Inicial', format_initial)
        if svls:
            for svl in svls:
                worksheet.write_number('L' + str(row), svl['quantity'], format_line_qty)
                worksheet.write_number('M' + str(row), svl['value'] / svl['quantity'], format_line_num)
                worksheet.write_number('N' + str(row), svl['value'], format_line_num)
                total_qty += svl['quantity']
                total_cost += svl['value']
        else:
            worksheet.write_number('L' + str(row), 0, format_line_qty)
            worksheet.write_number('M' + str(row), 0, format_line_num)
            worksheet.write_number('N' + str(row), 0, format_line_num)
            total_qty = 0
            total_cost = 0
        row += 1
        return row, total_qty, total_cost