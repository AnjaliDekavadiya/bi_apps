# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from .common_const import *
from odoo.exceptions import UserError, ValidationError

STR_TWO_DEGREE_ERROR = _("Field %s is have parent type %s. Can't have more than 2 degree for child field!")
STR_MANAGE_OBJECT_IMPORT_MODEL_UNIQUE =  _('This model is exist in other manage object. Please check it again!')

class ManageObjectImport(models.Model):
    _name = 'manage.object.import'
    _description = "Dinh nghia doi tuong nhap du lieu"
    
    name = fields.Char(string='Name',required=True)
    model_id = fields.Many2one('ir.model',string='Object to import data', required=True, ondelete='cascade')
    required_fields = fields.One2many('manage.field.import', 'manage_id', string='Required fields', 
                        domain=[('type','=','normal')], context={'default_type':'normal'})
    float_time_fields = fields.One2many('manage.field.import', 'manage_id',
                            string='Real number fields are displayed in hours and minutes format', 
                            domain=[('type','=','float_time')], context={'default_type':'float_time'})
    many_line_fields = fields.One2many('manage.field.import', 'manage_id', string='The many2many fields have values displayed line by line', 
                            domain=[('type','=','many2many')], context={'default_type':'many2many'})
    binary_real_fields = fields.One2many('manage.field.import', 'manage_id', string='The binary fields have value displayed as bytes string', 
                            domain=[('type','=','byte_str')], context={'default_type':'byte_str'})
    
    _sql_constraints = [('model_uniq', 'unique(model_id)', STR_MANAGE_OBJECT_IMPORT_MODEL_UNIQUE)]
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm gọi khi onchange model_id
    @api.onchange('model_id')
    def onchange_model_id(self):
        result = {
            'value':{'required_fields': [[6,0,[]]], 'float_time_fields': [[6,0,[]]], 'name': False},
            'warning':False
            }
        if self.model_id:
            check_model = self.search([('model_id','=',self.model_id.id)],limit=1)
            if check_model:
                warning = {'title': VKS_STR_WARNING,
                           'message' :STR_MANAGE_OBJECT_IMPORT_MODEL_UNIQUE
                           }
                result['warning'] = warning
            else:
                result['value']['name'] = self.model_id.name
        return result
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tìm kiếm các field float time của 1 model và các model con của nó
    @api.model
    def cal_list_float_time(self, model_id, list_float_time, dict_float_time):
        ir_model_pool = self.env['ir.model'].sudo()
        ir_model_field_pool = self.env['ir.model.fields'].sudo()
        result = []
        #Tìm và tạo data cho các field float_time của object
        for name_field in list_float_time:
            main_ft_field_objs = ir_model_field_pool.search([('model_id','=',model_id), ('name','=',name_field)], limit=1)
            if main_ft_field_objs:
                tmp_main_field = main_ft_field_objs[0]
                result.append([0, False, {'related_field':tmp_main_field.id, 'name':tmp_main_field.field_description, 'note':False}])
        #Tìm và tạo data cho các field float_time là field con của field one2many thuộc object
        for name_field in dict_float_time:
            ref_ft_field_objs = ir_model_field_pool.search([('model_id','=',model_id), ('name','=',name_field)],limit=1)
            if ref_ft_field_objs:
                tmp_ref_field = ref_ft_field_objs[0]
                model_objs = ir_model_pool.search([('model','=',tmp_ref_field.relation)])
                if model_objs:
                    list_child = dict_float_time.get(name_field, [])
                    for name_f in list_child:
                        f_child_objs = ir_model_field_pool.search([('model_id','=',model_objs[0].id), ('name','=',name_f)],limit=1)
                        if f_child_objs:
                            f_child = f_child_objs[0]
                            result.append([0, False, {'related_field':False, 'name':'%s/%s'%(name_field,name_f), 'note':f_child.field_description}])
        return result

class ManageFieldImport(models.Model):
    _name = 'manage.field.import'
    _description = "Dinh nghia cac truong nhap du lieu"
    
    manage_id = fields.Many2one('manage.object.import', string='Define the reference data import object', ondelete='cascade',required=True)
    related_field = fields.Many2one('ir.model.fields', string='Field')
    name = fields.Char(string='Technical name', required=True, help="""
- Specify the exact data field to import. 
- Use / if you want to define multi-level field, for example: job_id/salary_formula/code
""")
    note = fields.Char(string='Notes')
    type = fields.Selection([('normal','Normal'),('float_time','Float Time'),('many2many','Many2many'),
                             ('byte_str','Bytes String')], string='Type', default='normal')
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm gọi khi onchange related_field
    @api.onchange('related_field')
    def onchange_related_field(self):
        res = {'value': {'name':False, 'note':False}}
        if self.related_field:
            res['value']['name'] = self.related_field.name
        return res
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    @api.model
    def create(self, vals):
        vals = self.process_before_save(vals=vals,data_obj=False)
        new_obj = super(ManageFieldImport, self).create(vals)
        self.process_after_save(vals=vals,data_obj=new_obj)
        return new_obj
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    def write(self, vals):
        for data in self:
            tmp_vals = vals.copy()
            tmp_vals = self.process_before_save(vals=tmp_vals,data_obj=data)
            super(ManageFieldImport, data).write(tmp_vals)
            self.process_after_save(vals=tmp_vals,data_obj=data)
        return True
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý dữ liệu trước khi lưu
    @api.model
    def process_before_save(self,vals,data_obj):
        if 'related_field' in vals and vals.get('related_field',False):
            vals['name'] = self.env['ir.model.fields'].sudo().browse(vals.get('related_field')).name
        
        return vals
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý dữ liệu sau khi lưu
    @api.model
    def process_after_save(self, vals,data_obj):
        model_pool = self.env['ir.model'].sudo()
        tmp_type = data_obj.type
        tmp_manage_obj = data_obj.manage_id
        tmp_field_name = data_obj.name
        split_field_name = tmp_field_name.split('/')
        model_id = False
        is_first_field = True
        while len(split_field_name) > 0:
            if not model_id and is_first_field:
                model_id = tmp_manage_obj.model_id.id
            field = self._get_field_obj(field_name=split_field_name[0], model_id=model_id)
            if not field:
                raise UserError(_("Can't found field %s in system") % tmp_field_name)
            if is_first_field and len(split_field_name) > 1:
                if field.ttype == 'one2many':
                    if type == 'normal' and len(split_field_name) > 3:
                        raise UserError(_("Field %s is have parent type one2many. Can't have more than 3 degree for child field!") % tmp_field_name)
                    elif type == 'float_time' and len(split_field_name) > 2:
                        raise UserError(STR_TWO_DEGREE_ERROR % (tmp_field_name, field.ttype))
                elif field.ttype in ('many2one', 'many2many') and len(split_field_name) > 2:
                    raise UserError(STR_TWO_DEGREE_ERROR % (tmp_field_name, field.ttype))
                elif field.ttype not in ('many2one','many2many','one2many'):
                    raise UserError(_("Field %s with type %s. Can't have more than 1 degree!") % (tmp_field_name, field.ttype))
            elif tmp_type == 'float_time' and len(split_field_name) == 1 and field.ttype != 'float':
                raise UserError(_("Field %s not is a float time field!") % tmp_field_name)
            is_first_field = False
            field_model_objs = model_pool.search([('model','=',field.relation)],limit=1)
            model_id = field_model_objs and field_model_objs[0].id or False
            split_field_name.pop(0)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm dùng cho chức năng khác
    @api.model
    def _get_field_obj(self,field_name, model_id):
        field_objs = self.env['ir.model.fields'].sudo().search([('name', '=', field_name),('model_id', '=', model_id)],limit=1)
        return field_objs and field_objs[0] or False
    
