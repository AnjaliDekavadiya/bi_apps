'''
Created on Dec 11, 2018

@author: Zuhair Hammadi
'''
from odoo import models, _
from odoo.tools.safe_eval import safe_eval, wrap_module
from collections import OrderedDict, defaultdict
from xlsxwriter.utility import xl_col_to_name
import logging

_logger = logging.getLogger(__name__)

_rowno = '$rowno'

openpyxl = wrap_module(__import__('openpyxl'), {
    'styles' : ['Alignment', 'Border','Side', 'Color', 'PatternFill', 'GradientFill', 'Fill', 'Font', 'DEFAULT_FONT', 'NumberFormatDescriptor', 'NamedStyle', 'Protection'],
    'formula' : {
        'translate' : ['Translator']
        }
    })


class Base(models.AbstractModel):
    _inherit ='base'
    
    
    def get_excel_export(self, report_id, title = '', max_files = 30, action = True, pdf = None):  
        if isinstance(report_id, str):
            report_id = self.env.ref(report_id).id
        assert isinstance(report_id, int)
        report = self.env['oi_excel_export.config'].browse(report_id)
        if not report.seperate_rows:
            return self._get_excel_export(report, action=action, pdf= pdf)[0]
        ids = []
        slice_start = 0
        slice_stop = report.seperate_rows or None
        while len(ids) < max_files:
            action2, slice_next = self._get_excel_export(report, slice_start, slice_stop, pdf = False)
            if not slice_next or report.seperate_rows <=0:
                break
            if not action2 or not action2.get('type'):
                break
            ids.append(action2['params']['id'])
            slice_start += report.seperate_rows
            slice_stop += report.seperate_rows
            
        if action=='record':
            return ids
        
        if action=='object':
            return self.env['oi_excel_export'].browse(ids)
        
        
        return self.env['oi_excel_export'].browse(ids).merge(title = title, pdf = pdf if pdf is not None else report.pdf).action_download()        
                
    
    def _get_excel_export(self, report, slice_start = None, slice_stop = None, action = True, pdf = None):        
        rows = []        
        extra_rows = []
        data = self
        localdict = report._get_eval_context(self)
        localdict.update({
            'OrderedDict' : OrderedDict,
            'defaultdict' : defaultdict,
            'getcolname' : lambda s : report.line_ids.with_context(lang = 'en_US').filtered(lambda line : line.name == s)[:1].name,
            'xl_col_to_name' : xl_col_to_name,
            'openpyxl' : openpyxl,
            'report' : report,
            'slice_start' : slice_start,
            'slice_stop' : slice_stop,
            'slice_next' : False,
            '_logger' : _logger,           
            '_t' : _, 
            })
        parameters = {}
        if report.lines:            
            safe_eval(report.lines, localdict, mode='exec', nocopy=True)
            data = localdict.get('result', [])
            parameters = localdict.get('parameters') or {}
            rows = localdict.get('rows') or []
            extra_rows = localdict.get('extra_rows') or []
                                
        if not data and not rows:
            return {
                'message' : _('No data to print')
                }, False
        
        no = 0
        col_line_ids = report.line_ids
        for col in list(col_line_ids):
            if col.visible_condition:
                localdict['result'] = None
                safe_eval(col.visible_condition, localdict, mode='exec', nocopy=True)
                if not localdict.get('result'):
                    col_line_ids -= col                    
                    
        for dataline in data:
            no +=1
            row=OrderedDict()
            vals = {}
            localdict['vals'] = vals
            for col in col_line_ids:
                localdict.update({
                    'result' : None,
                    'result_seq' : 0,
                    'data' : dataline,
                    'line' : dataline,
                    'no' : report.crosstab and _rowno or no
                    })
                if col.value:
                    safe_eval(col.value, localdict, mode='exec', nocopy=True)
                result = localdict.get('result')
                result_seq = localdict.get('result_seq') or 0
                vals[col.name] = result
                if report.crosstab:
                    row[col.name]= (result_seq, result)
                else:
                    row[col.name]= result
            rows.append(row)
        
        rows.extend(extra_rows)
        
        header_rows_count = 1
        header_columns_count = 0
        row_merge_cells = []
        if report.crosstab and rows:
            header_rows = set()
            header_cols = set()
            crossdata = defaultdict(list)
            for datarow in rows:
                vals = defaultdict(list)
                for reportline in col_line_ids:
                    vals[reportline.crosstabloc].append(datarow[reportline.name])
                row = tuple(vals['row'])
                col = tuple(vals['col'])
                value = vals['value']
                value = value and value[0] or False
                header_rows.add(row)
                header_cols.add(col)
                crossdata[(row, col)].append(value)
            header_rows = sorted(header_rows)
            header_cols = sorted(header_cols)
            rows_count = len(header_rows[0])
            columns_count = len(header_cols[0])
            rows = []
            row_col_value = []
            for c in range(columns_count):
                row = []
                for index in range(rows_count):
                    if col_line_ids[index].show_title and c == columns_count-1:
                        row.append(col_line_ids[index].name)
                    else:
                        row.append('')
                rowno = len(rows)
                colno = rows_count
                for header_col in header_cols:
                    value = header_col[c]
                    if isinstance(value, tuple):
                        value = value[1]
                    row.append(value)       
                    row_col_value.append((rowno, colno, value))
                    colno +=1                                                 
                rows.append(row)
            
            last_rowno = -1
            last_colno = -1
            last_value = None
            last_merge = None
            for rowno, colno, value in row_col_value:
                if rowno == last_rowno and colno > last_colno and value == last_value:
                    if not last_merge or last_merge[3] != value:
                        if last_merge:
                            row_merge_cells.append(last_merge[:3])                        
                        last_merge = [rowno, last_colno, colno, value]
                    else:
                        last_merge[2] = colno
                last_rowno = rowno
                last_colno = colno
                last_value = value
            if last_merge:
                row_merge_cells.append(last_merge[:3])
                        
            rowno = 0
            for header_row in header_rows:                
                rowno +=1
                row = []
                for h in header_row:                    
                    if isinstance(h, tuple):
                        h = h[1]
                    if h is _rowno:
                        h = rowno + (slice_start or 0)                        
                    row.append(h)
                for header_col in header_cols:
                    
                    value = crossdata.get((header_row, header_col))                                            
                    if value:
                        if isinstance(value[0], tuple):
                            value = list(map(lambda v : v[1], value))
                        if isinstance(value[0], (float, int)):
                            value = sum(value)
                        elif len(value) > 1:
                            value = ','.join(map(str,value))
                        else:
                            value = value[0]
                    else:
                        value = None
                    row.append(value)
                rows.append(row)          
            header_rows_count = columns_count
            header_columns_count = rows_count
            
        default_parameters = { 'header_rows_count' : header_rows_count, 
                               'header_columns_count' : header_columns_count,
                               'row_merge_cells' : row_merge_cells,
                               'decimal_places' : report.decimal_places, 
                               'add_row_total' : report.add_row_total,
                               'add_column_total' : report.add_column_total,
                               'filename' : report.name,
                               'pdf' : pdf if pdf is not None else report.pdf,
                               'images' : report.get_images(),
                               'action' : action
                               }                
        
        for key, value in default_parameters.items():
            parameters.setdefault(key, value)
        
        return self.env['oi_excel_export'].export(rows, **parameters), localdict['slice_next']     