'''
Created on Dec 11, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import re
import uuid
from openpyxl.formula.translate import Translator

SUMMARY_FUNCTIONS = [('SUM','Sum'),
                     ('AVERAGE','Average'),
                     ('MIN','Minimum'),
                     ('MAX','Maximum'),
                     ('VAR.P','Population Variance (VAR.P)'),
                     ('VAR.S','Sample Variance (VAR.S)'),
                     ('STDEV.P','Population Standard Deviation (STDEV.P)'),
                     ('STDEV.S','Sample Standard Deviation (STDEV.S)'),
                     ('DEVSQ','Squared Deviation (DEVSQ)'),
                     ('AVEDEV','Average Absolute Deviation (AVEDEV)'),
                     ('MAD','Median Absolute Deviation (MAD)'),
                     ]

def normilize(*names):
    name = ' '.join(names)
    return re.sub('\W',' ', name.lower()).strip().replace(' ', '_')     

class ReportConfig(models.Model):
    _name = 'oi_excel_export.config'
    _description = 'oi_excel_export.config'
    _order='name'
    
    name = fields.Char(required = True)
    lines = fields.Text('Python Code')
    model_id = fields.Many2one('ir.model', string='Object', required = True, ondelete='cascade')    
    action_id = fields.Many2one('ir.actions.server', string='Action', readonly = True, copy = False)
    
    line_ids = fields.One2many('oi_excel_export.line', 'report_id', copy = True)
    image_ids = fields.One2many('oi_excel_export.image', 'report_id', copy = True)
    line_count = fields.Integer(compute = '_calc_line_count')
    
    decimal_places = fields.Integer(default =2)
    
    crosstab = fields.Boolean()
    
    add_row_total = fields.Selection(SUMMARY_FUNCTIONS, default = 'SUM')
    add_column_total = fields.Selection(SUMMARY_FUNCTIONS)
    
    pdf = fields.Boolean('PDF')
    
    seperate_rows = fields.Integer()
    
    @api.depends('line_ids')
    def _calc_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)
    
    
    def _get_eval_context(self, record):
        user = self.env.user
        vals = self.env['ir.actions.actions']._get_eval_context()
        
        def insert_rows(ws, shift_rows = 1):
            ws.insert_rows(0, shift_rows)
          
            for row in ws.rows:
                for cell in row:
                    if cell.data_type == "f":
                        t = Translator(cell.value, cell.coordinate)
                        value= t.translate_formula(row_delta=shift_rows, col_delta=0)   
                        cell.value = value                 
        
        vals.update({
            'user' : user,
            'uid' : user.id,
            'record' : record,
            'object' : record,
            'self' : record,
            'env' : self.env,
            'relativedelta' : relativedelta,
            'Date' : fields.Date,
            'Datetime' : fields.Datetime,
            'insert_rows' : insert_rows
            })
        return vals
    
    
    
    def create_action(self):
        xml_id = self.get_external_id().get(self.id)
        if not xml_id:
            vals = {'module' : '_',
                    'name' : normilize(self._name, self.display_name),
                    'res_id' : self.id,
                    'model' : self._name
                    }
            while self.env.ref('%(module)s.%(name)s' % vals, False):
                vals['name'] = '%s_%s' % (vals['name'], uuid.uuid4().hex[:6])
                
            xml_id=self.env['ir.model.data'].create(vals).complete_name
        vals = {
            'name' : self.name,
            'state': 'code',
            'model_id' : self.model_id.id,
            'binding_model_id' : self.model_id.id,
            'binding_type' : 'report',
            'code' : 'action=records.get_excel_export("%s")' % xml_id
            }
        if self.action_id:
            self.action_id.write(vals)
        else:
            self.action_id = self.action_id.create(vals)
    
    
    def remove_action(self):
        self.action_id.unlink()
        
    
    def unlink(self):
        self.mapped('action_id').unlink()
        return super(ReportConfig, self).unlink()
    
    
    def write(self, vals):
        res = super(ReportConfig, self).write(vals)
        if 'name' in vals:
            for record in self:
                record.action_id.write({'name' : record.name})
        return res
    
    
    def get_images(self):
        res = []
        for image in self.image_ids:
            vals = {                
                'cell' : image.cell,
                'data' : image.data,
                'dimensions' : {
                        'x_offset' : image.offset_x,
                        'y_offset' : image.offset_y,
                        'x_scale' : image.scale_x,
                        'y_scale' : image.scale_y,
                    }
                }            
            res.append(vals)
        return res
    
    
    def action_lines(self):
        return {
          'type' : 'ir.actions.act_window',
          'name' : 'Columns',
          'view_mode' : 'tree,form',
          'view_type' : 'form',
          'res_model' : 'oi_excel_export.line',
          'domain' : [('report_id', '=', self.id)],
          'context' : {
            'default_report_id' : self.id
          }
        }        