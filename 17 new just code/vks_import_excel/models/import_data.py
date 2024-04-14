# -*- coding: utf-8 -*-
 
from odoo import api, fields, models, _
from .common_const import *
from odoo.exceptions import UserError, ValidationError
from odoo import tools
from datetime import datetime
import xlrd
import base64
import threading
import time
import logging

log = logging.getLogger(__name__)

IMPT_NEW_ID_VALUE = 'new'
IMPT_DEL_ALL_ONE2MANY_ID = 'DELETE'
IMPT_DEL_ID_SUFFIXES = 'DEL_ROW'
IMP_DEL_ROW_KEY = 'NEED_DEL_ROW'
IMP_DELL_MANY2MANY = 'DELL_MANY2MANY_KEY'
 
FORMAT_DATETIME_VN = "%d/%m/%Y %H:%M:%S"

class ImportData(models.Model):
    _name = 'import.data'
    _inherit = 'vks.process.by.thread.basic'
    _description = 'Nhap du lieu tu file'
    _order = 'write_date desc'
    
    #Thêm bởi Tuấn - 02/10/2023
    def _count_status(self):
        imp_status_pool = self.env['import.data.status']
        for child_item in self:
            tmp_count = imp_status_pool.search_count([('import_id', '=', child_item.id)])            
            child_item.read_count = tmp_count or 0
            
    name = fields.Char(string='Name',required=True,readonly=False)
    model_name = fields.Char(string='Object to import data (technical name)',readonly=True)
    model_id = fields.Many2one('ir.model', string='Object to import data', required=True,ondelete='cascade')
    file_import = fields.Binary(string='Data import file', required=True)
    file_name = fields.Char(string='File name')
    total_row = fields.Integer('Total records', help="Total records to process",readonly=True)
    current_row = fields.Integer(string='Current row', help="Current processing row",readonly=True)
    success_row = fields.Integer(string='Number of successful records', help="Number of records processed successfully",readonly=True)
    read_count = fields.Integer(string='Number of records processed', compute='_count_status',readonly=True)
    status_ids = fields.One2many('import.data.status','import_id',string='Data import result',readonly=True)
    
    #Thêm bởi Tuấn - 02/10/2023
    @api.model
    def default_get(self, fields):
        vks_context = dict(self._context) or {}
        result = super(ImportData, self).default_get(fields)
        if 'model_name_tmp' in vks_context:
            result['model_name'] = vks_context.get('model_name_tmp', False)
            model_objs = self.env['ir.model'].search([('model', '=', result['model_name'])],limit=1)
            result['model_id'] = model_objs and model_objs[0].id or False
        return result
 
    #Thêm bởi Tuấn - 02/10/2023
    @api.onchange('model_id')
    def onchange_model_id(self):
        res = {'value': {'name': False}}
        if self.model_id:
            model_name = self.model_id.name
            datenow = datetime.strftime(datetime.now(), FORMAT_DATETIME_VN)
            res['value']['name'] = 'Import '+ model_name + ' ' + datenow
        return res
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    @api.model
    def create(self,vals):
        if 'manage_id' in vals and vals.get('manage_id',False):
            manage_obj =  self.env['manage.object.import'].browse(vals.get('manage_id'))
            vals['model_name'] = manage_obj.model_id.name
            vals['model_id'] = manage_obj.model_id.id
        return super(ImportData, self).create(vals)
    
    #Thêm bởi Tuấn - 20/11/2023 - Hàm lấy nội dung thông báo lỗi khi giá trị field không tồn tại
    @api.model
    def get_f_val_not_found_err(self):
        return _('Field %s - Value %s not found in system!')
    
    #Thêm bởi Tuấn - 20/11/2023 - Hàm lấy nội dung thông báo lỗi khi field bắt buộc nhập giá trị
    @api.model
    def get_f_required_err(self):
        return _('Field %s - Value must be required!')
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm kiểm tra các field bắt buộc nhập
    @api.model
    def check_required_field(self, fields_name, row, required_fields=[]):
        inconsistance_fields = []
        for index, field_name in enumerate(fields_name):
            field_name = field_name.split('/')[0]            
            field_value = u"%s" % row[index]
            #field_value = field_value.strip()
            if field_value == 'False':
                field_value = ''
            if field_name in required_fields and not field_value:
                inconsistance_fields.append(field_name)
        if inconsistance_fields:
            return_message = self.get_f_required_err() % ",".join(inconsistance_fields)
            return return_message
        return ""
     
    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuyển đổi xldate value trong excel sang datetime
    @api.model
    def xldate_to_datetime(self, cell_value,type='datetime'):
        #Chuyển đổi excel value sang datetime
        datetime_value = datetime(*xlrd.xldate_as_tuple(cell_value, 0))
        #Chuyển datetime_value về string và return
        res_val = False
        if type =='date':
            res_val = datetime.strftime(datetime_value,tools.DEFAULT_SERVER_DATE_FORMAT)
        else:
            res_val = datetime.strftime(datetime_value,tools.DEFAULT_SERVER_DATETIME_FORMAT)
        return res_val
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm nhận giá trị mà không có số không
    @api.model
    def get_value_without_zeros(self, temp_value=False):
        try:
            if temp_value % 1 == 0:
                temp_value = '%.f' % temp_value
        except Exception as e:
            pass
        return temp_value
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy id record thông qua giá trị cột id trong file excel
    @api.model
    def get_record_id_by_id_value(self, search_pool, id_value):
        result = False
        if id_value:
            model_data_pool = self.env['ir.model.data']
            refrence_split = id_value.split(VKS_SPLIT_XML_ID_CHAR)
            if len(refrence_split) < 2:
                try:
                    search_objs = search_pool.search([('id','=',id_value)])
                    result = search_objs and search_objs[0].id or False
                except Exception as e:
                    self._cr.rollback()
                    result = False
            else:
                try:
                    result = model_data_pool.get_object_reference(refrence_split[0], refrence_split[1])[1]
                except Exception as e:
                    result = False
        return result
 
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tìm kiếm id bản ghi phù hợp giá trị trong 1 model
    @api.model
    def search_record_id_by_field_value(self, model_pool, fieldname, field_search_by,cell_value):
        res_vals = {'record_id':False,'error_mess':False}
        try:
            if str(cell_value)=='':
                res_vals['record_id'] = False
                return res_vals
            
            item_objs = model_pool.search([(field_search_by, '=', cell_value)])
            if not item_objs:
                res_vals['error_mess'] = (self.get_f_val_not_found_err() % (fieldname,cell_value))
            else:
                #Nếu chỉ có 1 giá trị phù hợp
                if len(item_objs) == 1:
                    res_vals['record_id'] = item_objs[0].id
                else:
                    res_vals['error_mess'] = (_('Field %s - Exist multiple record compatible value %s') % (fieldname,cell_value))
        except Exception as e:
            res_vals['error_mess'] = str(e)
        return res_vals
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm phân tách giá trị của many2many value
    @api.model
    def make_arr_value_for_many2many(self, cell_value):
        if not cell_value:
            return [cell_value]
        return cell_value.split(VKS_STR_SPLIT_MANY2MANY_VALUES)
        
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tìm kiếm id bản ghi phù hợp giá trị trong 1 model theo display_name
    @api.model
    def search_record_id_by_name_get_value(self, model_pool, fieldname,field_type, cell_value):
        res_vals = {'record_ids':[],'error_mess':False}
        try:
            tmp_error_val = ''
            arr_val = False
            if field_type !='many2many':
                arr_val = [cell_value]
            else:
                arr_val = self.make_arr_value_for_many2many(cell_value=cell_value)
            
            tmp_record_ids = []
            tmp_valid_arr = []
            tmp_not_valid_count = 1
            tmp_nget_all = False
            tmp_offset = 0
            while tmp_offset !=-1:
                tmp_nget_all = model_pool.search([],order='id asc',offset=tmp_offset,limit=2018).name_get()
                if not tmp_nget_all or len(tmp_nget_all)==0:
                    break
                for nget in tmp_nget_all:
                    if tmp_not_valid_count == 0:
                        break
                    tmp_not_valid_count = len(arr_val)
                    for child_val in arr_val:
                        if child_val in tmp_valid_arr:
                            tmp_not_valid_count -= 1
                            continue
                        if nget[1] == child_val:
                            tmp_record_ids.append(nget[0])
                            tmp_valid_arr.append(child_val)
                            tmp_not_valid_count -= 1
                            continue
                
                if tmp_not_valid_count != 0:
                    tmp_offset += 2018
                else:
                    tmp_offset = -1
                
            #Nếu dự báo có thể có lỗi
            if tmp_not_valid_count > 0:
                for c_str in arr_val:
                    if c_str not in tmp_valid_arr:
                        tmp_error_val += '%s,' % (c_str)
            #Nếu thực sự có lỗi
            if tmp_error_val!='':
                tmp_error_val = tmp_error_val[:-1]
                res_vals['error_mess'] = (self.get_f_val_not_found_err() % (fieldname,tmp_error_val))
            res_vals['record_ids'] = tmp_record_ids
        except Exception as e:
            res_vals['error_mess'] = str(e)
        return res_vals
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy các giá trị cho 1 field kiểu selection
    @api.model
    def get_selection_of_field(self, field_name=False, model=False):
        dict_temp =  {}
        try:
            dict_temp = dict(self.env[model].fields_get([field_name])[field_name]['selection'])
        except Exception as e:
            pass
        return dict_temp
     
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy key của field selection thông qua key hoặc value
    @api.model
    def get_key_with_selection(self, temp_value=False, field_name=False, model=False):
        res_selection_key = False
        selection_temp = self.get_selection_of_field(field_name=field_name, model=model)
        if temp_value and selection_temp:
            for child_key,child_value in selection_temp.items():
                if temp_value == str(child_key) or temp_value == str(child_value):
                    res_selection_key = child_key
                    break
        return res_selection_key  
     
    #Thêm bởi Tuấn - 02/10/2023 - Hàm kiểm tra field bắt buộc nhập do người dùng quy định thay vì quy định trong code
    @api.model
    def check_required_for_special_field(self, field_name, vals_fields, required_special={}, current_row=0, id_o2m_before = False):
        message = ""
        if vals_fields.get('id'):
            if not required_special.get(field_name) is None:
                for required in required_special.get(field_name):
                    m_temp = ""
                    required_tmp = required.split('/')[-1]
                    if required_tmp in vals_fields:
                        value_tmp = vals_fields[required_tmp]
                        if value_tmp == False and type(value_tmp) not in (int, float):
                            m_temp = self.get_f_required_err() % (required)
                    if len(m_temp):
                        message += len(message) == 0 and m_temp or VKS_NORMAL_NEW_LINE_CHAR + m_temp
        elif not id_o2m_before:
            mess = self.get_f_required_err() % (field_name + '/id')
            message += len(message) == 0 and mess or VKS_NORMAL_NEW_LINE_CHAR + mess
        if len(message):
            message = _("Row %s : %s") % (current_row, message)
        return message
    
    #Thêm bởi Tuấn - 23/10/2023 - Hàm chuẩn hóa dữ liệu kiểu json
    @api.model
    def vks_standardized_json_data(self, cell_value, json_dict_field):
        json_vals = self.env['common.method'].vks_convert_string_to_dict(str_org_dict=cell_value)
        tmp_val = False
        json_pool = json_dict_field['json_pool']
        json_des = json_dict_field['json_des']
        json_search_f = json_dict_field['json_search_f']
        json_search_d = json_dict_field['json_search_d']
        tmp_s_dict = {}
        tmp_error_str = ''
        #Kiểm tra rà soát các giá trị người dùng nhập sai
        for child_key, child_values in json_vals.items():
            try:
                tmp_val = json_pool.search([('id','=',int(child_key))],limit=1)
                if not tmp_val:
                    tmp_error_str += VKS_NORMAL_NEW_LINE_CHAR + _('No %s with id = %s exists') % (json_des, child_key)
            except Exception as e:
                tmp_val = json_pool.search([(json_search_f,'=',child_key)])
                if not tmp_val:
                    tmp_error_str += VKS_NORMAL_NEW_LINE_CHAR + _("""No %s with %s = '%s' exists""") % (json_des, json_search_d, child_key)
                else:
                    if len(tmp_val)==1:
                        #Lưu lại để đổi key sau khi hết vòng for
                        tmp_s_dict.update({str(tmp_val[0].id):child_key})
                    else:
                        tmp_error_str += VKS_NORMAL_NEW_LINE_CHAR + _("""Exist multiple %s with %s = '%s' """) % (json_des, json_search_d, child_key)
        if tmp_error_str!='':
            json_vals = False
        else:
            #Thay đổi key về integer nếu cần
            if tmp_s_dict:
                for new_key, old_key_val in tmp_s_dict.items():
                    json_vals.update({new_key:json_vals.pop(old_key_val)})
                    
        return {'cell_value':json_vals,'error_mess':tmp_error_str}
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo kết quả import
    @api.model
    def create_detail_import(self, detail_pool=None, import_id=False, row=0, message=False, status='success', type=False):
        vks_context = dict(self._context) or {}
        local_context = vks_context.copy()
        if detail_pool is None:
            detail_pool = self.env['import.data.status']
        if not type:
            type = 'exc'
        if not message and status=='success':
            if type == 'create':
                message =  _('Create record success.')
            elif type =='write':
                message = _('Update record success.')
            elif type =='delete':
                message = _('Delete record success.')
        #Nếu loại là lỗi thì không tính lại các field function
        if type == 'exc':
            local_context.update({'recompute':False})
        vals = {
            'import_id': import_id,
            'row_number': row,
            'message': message,
            'status': status,
            'type': type,
                }
        detail_id = detail_pool.with_context(local_context).create(vals)
        self._cr.commit()
        return detail_id
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy giá trị của 1 cell
    @api.model
    def get_value_one_cell(self, row_index, index_column, cell_value, temp_cell, 
                           name_field, create_pool, float_time_fields=[], dict_field_tmp={}):
        res = {'message':""
               }
        message = ""
        #Tên field
        field_name = dict_field_tmp[name_field]['name']
        #Kiểu field 
        field_type = dict_field_tmp[name_field]['ttype'] 
        #Model field
        field_model = dict_field_tmp[name_field]['model_id'] 
        tmp_ref_pool = False
        #Tìm Relation pool cho kiểu many2one,one2many,many2many
        field_relation_pool = False
        tmp_ref_pool = dict_field_tmp[name_field]['relation']
        if tmp_ref_pool:
            field_relation_pool = self.env[tmp_ref_pool]
        #Field sẽ được tìm kiếm theo
        field_search_by = dict_field_tmp[name_field]['search_by'] 
        #Kiểu field cha
        parent_type_field = dict_field_tmp[name_field]['parent_ttype'] 
        #Relation field cha
        parent_relation_field_pool = False
        tmp_ref_pool = dict_field_tmp[name_field]['parent_relation']
        if tmp_ref_pool:
            parent_relation_field_pool = self.env[tmp_ref_pool]
        #Nếu value trên ô excel là rỗng
        if temp_cell.ctype == xlrd.XL_CELL_EMPTY:
            #Chỉ tự động điền giá trị khi là kiểu boolean để không làm ảnh hưởng đến các giá trị mặc định trong trường hợp create
            if field_type == 'boolean':
                res['cell_value'] = False
            return res
        
        #Nếu giá trị ô trong excel là FALSE (muốn thiết lập về rỗng trong 1 số trường hợp nhất là khi write)
        if str(temp_cell.value) == '0':
            if field_type != 'one2many':
                if field_type in ('integer','float','monetary'):
                    res['cell_value'] = 0
                elif field_type=='many2many':
                    res['cell_value'] = IMP_DELL_MANY2MANY
                else:
                    res['cell_value'] = False
            
            return res
        
        #Nếu là ID column
        if name_field == 'id' or field_name == 'id' or field_search_by == 'id':
            search_pool = create_pool
            #Nếu field cha là kiểu many2many: value có dạng id1,id2,....
            if parent_type_field == 'many2many' or dict_field_tmp[name_field].get('m2m_export_mode','test')=='one_line':
                search_pool = parent_relation_field_pool
                split_values = self.make_arr_value_for_many2many(cell_value=cell_value) 
                message_many2many = []
                many2many_ids = []
                for split_value in split_values:
                    res_id = self.get_record_id_by_id_value(search_pool=search_pool, id_value=split_value)
                    if res_id:
                        many2many_ids.append(res_id)
                    else:
                        message_many2many.append(split_value)
                if message_many2many:
                    str_values = ''
                    for value in message_many2many:
                        value = value.encode('utf-8').decode('utf-8')
                        str_values += len(str_values) == 0 and value or ','+value
                    message = self.get_f_val_not_found_err() % (name_field, str_values)
                else:
                    if dict_field_tmp[name_field]['m2m_export_mode']=='one_line':
                        cell_value = [(6, 0, many2many_ids)]
                    else:
                        cell_value = many2many_ids[0]
            else:
                if parent_type_field =='one2many':
                    search_pool = parent_relation_field_pool
                elif parent_type_field == 'many2one':
                    search_pool = field_relation_pool
                if temp_cell.value == 0:
                    cell_value = False
                #Nếu không phải tạo mới object
                elif cell_value != IMPT_NEW_ID_VALUE:
                    #Nếu không phải là xóa toàn bộ đối với kiểu one2many thì tìm EX ID phù hợp 
                    if cell_value!=IMPT_DEL_ALL_ONE2MANY_ID:
                        #Xem xét có phải là xóa chỉ riêng dòng đó hay không
                        if cell_value.endswith(IMPT_DEL_ID_SUFFIXES):
                            res[IMP_DEL_ROW_KEY] = True
                            tmp_leng_suffix = len(IMPT_DEL_ID_SUFFIXES)
                            cell_value = cell_value[:-tmp_leng_suffix]
                        #Tìm ID phù hợp để xóa hoặc cập nhật
                        res_id = self.get_record_id_by_id_value(search_pool=search_pool, id_value=cell_value)
                        if res_id:
                            cell_value = res_id
                        else:
                            message = self.get_f_val_not_found_err() % (name_field, cell_value)
                #Nếu cột id có giá trị là IMPT_NEW_ID_VALUE và thuộc kiểu many2one
                elif field_type == 'many2one':
                    cell_value = False
                    message = _('Field %s is type many2one can not search with value %s') % (name_field,IMPT_NEW_ID_VALUE)
        #Nếu kiểu field là boolean
        elif field_type == 'boolean':
            cell_value = bool(temp_cell.value)
        #Nếu kiểu field là float
        elif field_type in ('float','monetary'):
            try:
                cell_value = float(cell_value)
            except Exception:
                message = _('Field %s - Value must be number!') % (name_field)
            if name_field in float_time_fields:
                cell_value = cell_value * 24
        #Nếu kiểu field là integer
        elif field_type == 'integer':
            try:
                cell_value = int(cell_value)
            except Exception:
                message = _('Field %s - Value must be integer!') % (name_field)
        #Nếu kiểu field là kiểu datetime hoặc date
        elif field_type == 'datetime' or field_type == 'date':
            if temp_cell.ctype != 3:
                message = _('Field %s - Value must be has format with date!') % (name_field)
            else:
                cell_value = self.xldate_to_datetime(cell_value=temp_cell.value,type=field_type)
        #Nếu kiểu field là kiểu selection
        elif field_type == 'selection':
            key_selection = self.get_key_with_selection(temp_value=cell_value, field_name=field_name, model=field_model.model)
            if key_selection:
                cell_value = key_selection
            else:
                message = self.get_f_val_not_found_err() % (name_field, cell_value)
        elif field_type in ('many2one', 'many2many'):
            if field_search_by:
                tmp_vals = self.search_record_id_by_field_value(model_pool=field_relation_pool, fieldname=name_field,
                                        field_search_by=field_search_by, cell_value=cell_value)
                if tmp_vals['error_mess'] == False:
                    cell_value = tmp_vals['record_id']
                else:  
                    message = tmp_vals['error_mess']
            else:
                relation_pool = parent_relation_field_pool
                #Nếu là field con
                if parent_type_field == 'one2many': 
                    relation_pool = field_relation_pool
                model_objs = relation_pool.search([])
                if field_type in ('many2one','many2many'):
                    tmp_vals = self.search_record_id_by_name_get_value(model_pool=relation_pool, fieldname=name_field, 
                                        field_type=field_type, cell_value=cell_value)
                    if tmp_vals['error_mess']==False:
                        if field_type == 'many2one':
                            cell_value = tmp_vals['record_ids'][0]
                        else:
                            if dict_field_tmp[name_field]['m2m_export_mode']=='one_line':
                                cell_value = [(6, 0, tmp_vals['record_ids'])]
                            else:
                                cell_value = tmp_vals['record_ids'][0]
                    else:
                        message = tmp_vals['error_mess']
                        cell_value = False
        elif field_type=='binary':
            try:
                if dict_field_tmp[name_field]['b_param']['b_mode']=='url':
                    tmp_is_image = False
                    if dict_field_tmp[name_field]['b_param']['b_type']=='image':
                        tmp_is_image = True
                    res['cell_ctx'] = {'r_model_name':field_model.model,'r_field_name':field_name,'r_url':cell_value}
                    cell_value = self.env['common.method'].make_base64_string_from_url(f_url=cell_value,valid_image_size=tmp_is_image)
                else:
                    cell_value = bytes(cell_value,'utf-8')
            except Exception as e:
                cell_value = False
                message = str(e)
        elif field_type=='json':
            tmp_json_res = self.vks_standardized_json_data(cell_value=cell_value, json_dict_field=dict_field_tmp[name_field])
            cell_value = tmp_json_res['cell_value']
            message = tmp_json_res['error_mess']
        res['cell_value'] = cell_value
        if message!="":
            message = _("""Row %s column %s : %s""") % (row_index +1, index_column +1, message)
             
        res['message'] = message
        return res
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy giá trị của cả 1 dòng
    @api.model
    def get_values_one_row(self, row, name_fields, model_id, model_create, sheet, row_index, float_time_fields=[], dict_field_tmp={},
                            is_child=False, list_field_has_child=[]):
        
        create_pool = self.env[model_create]
        o2m_tmp = {}
        m2m_keys = []
        m2m_in_o2m = {}
        res = {'values': {},
            'success': True,
            'message': "",
            'row_ctx':{}
        }
        message = ""
        list_name_fields = is_child and list_field_has_child or name_fields
        for index, name_field in enumerate(list_name_fields):
            index_column = is_child and dict_field_tmp[name_field]['index_column'] or index
            temp_cell = sheet.cell(row_index, index_column)
            field_value = self.get_value_without_zeros(temp_value=temp_cell.value)
             
            dict_get = self.get_value_one_cell(row_index = row_index, index_column = index_column,
                                    cell_value = field_value, temp_cell = temp_cell, 
                                    name_field = name_field, create_pool = create_pool, 
                                    float_time_fields = float_time_fields, dict_field_tmp = dict_field_tmp)
            
            #Nếu là xóa toàn bản ghi
            if name_field == 'id' and dict_get.get(IMP_DEL_ROW_KEY,False):
                res['values'] = {IMP_DEL_ROW_KEY:True,'id':dict_get.get('cell_value',-1)}
                break
            #Ngược lại
            elif 'cell_value' in dict_get:
                if dict_field_tmp[name_field]['parent_ttype'] not in ('many2many','one2many'):
                    res['values'][dict_field_tmp[name_field]['name']] = dict_get.get('cell_value')
                elif dict_field_tmp[name_field]['parent_ttype'] == 'one2many':
                    str_tmp_key = dict_field_tmp[name_field]['parent_name']
                    if str_tmp_key not in o2m_tmp:
                        o2m_tmp[str_tmp_key] = {}
                    
                    o2m_tmp[str_tmp_key].update({dict_field_tmp[name_field]['name']:dict_get.get('cell_value')
                                                })
                    
                    if IMP_DEL_ROW_KEY in dict_get:
                        o2m_tmp[str_tmp_key].update({IMP_DEL_ROW_KEY: dict_get[IMP_DEL_ROW_KEY]})
                                                                                
                    if dict_field_tmp[name_field]['ttype'] == 'many2many' and dict_field_tmp[name_field]['name'] not in m2m_in_o2m:
                        m2m_in_o2m.update({dict_field_tmp[name_field]['name']:name_field})
                elif dict_field_tmp[name_field]['parent_ttype'] == 'many2many':
                    if dict_field_tmp[name_field]['m2m_export_mode'] == 'many_line' or str(dict_get['cell_value'])==IMP_DELL_MANY2MANY:
                        if dict_field_tmp[name_field]['name'] not in m2m_keys:
                            m2m_keys.append(dict_field_tmp[name_field]['name'])
                    res['values'].update({
                                    dict_field_tmp[name_field]['parent_name']: dict_get.get('cell_value')
                                          })
            else:
                if dict_field_tmp[name_field]['ttype'] == 'many2many' and dict_field_tmp[name_field]['parent_ttype'] == 'one2many' and dict_field_tmp[name_field]['name'] not in m2m_in_o2m:
                    m2m_in_o2m.update({dict_field_tmp[name_field]['name']:name_field})
            #Cập nhật message
            if dict_get.get('message', False):
                res.update({'success': False})
                message += len(message) == 0 and dict_get.get('message', "") or VKS_NORMAL_NEW_LINE_CHAR + dict_get.get('message', "")
            #Xử lý context
            if 'cell_ctx' in dict_get:
                tmp_model_name = dict_get['cell_ctx'].pop('r_model_name')
                if tmp_model_name not in res['row_ctx']:
                    res['row_ctx'][tmp_model_name] = {}
                res['row_ctx'][tmp_model_name][dict_get['cell_ctx']['r_field_name']] = dict_get['cell_ctx']['r_url']
            
        res['o2m_keys'] = o2m_tmp.keys()
        res['m2m_keys'] = m2m_keys
        res['m2m_in_o2m'] = m2m_in_o2m
        for o2m_key in res['o2m_keys']:
            res['values'][o2m_key] = [(0,0,o2m_tmp[o2m_key])]
        res['message'] = message
        return res
     
    #Thêm bởi Tuấn - 02/10/2023 - Hàm kiểm tra dòng chứa one2many có rỗng hay ko
    @api.model
    def check_line_one2many_empty(self, sheet, one2many_key, list_fields=[], dict_field_tmp={}, row_index=0):
        is_empty = True
        for name_field in list_fields:
            parent_ttype = dict_field_tmp[name_field]['parent_ttype']
            parent_name = dict_field_tmp[name_field]['parent_name']
            f_name = dict_field_tmp[name_field]['name']
            if parent_ttype == 'one2many' and parent_name == one2many_key and f_name != 'id':
                index_column = dict_field_tmp[name_field]['index_column']
                temp_cell = sheet.cell(row_index, index_column)
                if temp_cell.ctype != xlrd.XL_CELL_EMPTY:
                    is_empty = False
                    break
        return is_empty
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo trạng thái import mới
    @api.model
    def make_new_import_state(self,current_row=0,total_row=0,need_commit=True):
        tmp_vals = {'process_state': 'doing', 'current_row': current_row, 'total_row': total_row}
        #Nếu bắt đầu xử lý từ dòng đầu tiên thì xóa hết các kết quả import liên quan 
        if current_row==0 and self.status_ids:
            tmp_vals.update({'success_row':0})
            self.status_ids.unlink()
        #Chuyển trạng thái đang xử lý
        self.write(tmp_vals)
        if need_commit:
            self._cr.commit()
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm import data bằng thread
    @api.model
    def thread_general_import_common(self, sheet=False, required_fields=[], o2m_required_fields={}, float_time_fields=[]):
        vks_context = dict(self._context) or {}
        local_context = vks_context.copy()
        local_context.update({'is_validate_import_extra':False,'active_test':False,'vks_import_ex_thread':True})
        common_method_pool = self.env['common.method']
        
        try:
            tmp_thread_vals = common_method_pool.get_var_using_in_thread(get_cursor=True,get_env=True,extend_context=local_context)
            new_cr = tmp_thread_vals['new_cr']
            new_env = tmp_thread_vals['new_env']
            self_extend_pool = new_env['import.data']
            ir_model_pool = new_env['ir.model'].sudo()
            ir_fields_pool = new_env['ir.model.fields'].sudo()
            menu_pool = new_env['ir.ui.menu'].sudo()
            
            record = self_extend_pool.browse(self.id)
            record.write({'process_state': 'doing','vks_thread_start_time': datetime.utcnow()})
            new_cr.commit()
            model_id = record.model_id.id
            model_create = record.model_id.model
            create_pool = new_env[model_create]
            if not sheet:
                #read file excel
                book = False
                path = common_method_pool.save_file(name=record.file_name, value=record.file_import)
                try:
                    book = xlrd.open_workbook(path) 
                except:
                    record.make_new_import_state()
                    self_extend_pool.create_detail_import(import_id=record.id, message=_('File not found!. Please check path...'), status='fail')
                finally:
                    pass
                sheet=book.sheet_by_index(0)
            from_row = 3                
            total_row = 0
            #Kiem tra cot A co phai la cot id hay khong
            cell_id = sheet.cell(0,0)
            if cell_id.value != 'id':
                message=_("The value of cell [A:0] must be id")
                self_extend_pool.create_detail_import(import_id=record.id, row=0, message=message, status='fail')
                record.write( {'process_state': 'error'})
                new_cr.commit()
                return True
            
            tmp_total_s_row = sheet.nrows
            #Kiem tra cot A co dong nao co du lieu hay khong
            for r in range(from_row, tmp_total_s_row):
                if sheet.cell(r,0).value:
                    total_row += 1
            if total_row == 0:
                message=_("Don't have row has define of id ('%s' or external_id or id) in columns A") % (IMPT_NEW_ID_VALUE)
                self_extend_pool.create_detail_import(import_id=record.id, row=0, message=message, status='fail')
                record.write({'process_state': 'error'})
                new_cr.commit()
                return True
            
            current_row = 0
            row_counter = 2 #Dòng hiện tại
            success_row = 0 #Số dòng thành công
            #Nếu là trường hợp đang import bị ngắt ngang phải import lại
            if record.current_row > 0:
                current_row = record.current_row 
                from_row = current_row
                #row_counter phải set theo index đánh từ 0 của xlrd thay vì current_row đánh từ 1 dạng mắt xem thông thường
                row_counter = from_row - 1
                success_row = record.success_row
            
            #Chuyển trạng thái đang xử lý
            record.make_new_import_state(current_row=current_row,total_row=total_row)
            
            is_child = False #Là dòng con
            not_error = True
            data_temp = {}
            id_o2m_before = False
            message = ""
             
            name_fields = sheet._cell_values[0][0:sheet.ncols]
            if '' in name_fields:
                not_error = False
                message=_("Cell define column import is blank. Please check again!")
                self_extend_pool.create_detail_import(import_id=record.id, row=0, message=message, status='fail')
                record.write( {'process_state': 'error'})
                new_cr.commit()
                return True
            else:
                #Lấy thông tin của field được define trong file excel
                list_field_has_child = [] #Mô tả các cột có dữ liệu trên nhiều dòng: one2many hoặc many2many nhưng tìm kiếm không theo id
                list_field_m2m_m2o = [] #Mô tả các cột chỉ được phép có đúng 1 cột trong file.
                dict_field_tmp = {}
                is_error_when_check = False #Lỗi không tìm thấy field trong khi lấy thông tin column
                list_m2m_m2o_error = ''
                list_column_error = ''
                index_column = 0
                for field_name in name_fields:
                    tmp_model_id = record.model_id.id
                    name_splits = field_name.split('/')
                    if name_splits[0] not in dict_field_tmp:
                        dict_field_tmp.update({field_name:{
                                                'name':False,#Tên field
                                                'ttype':False,#Kiểu field
                                                'relation':False,#Model relation
                                                'parent_name':False,#Tên field cha
                                                'parent_ttype':False,#Kiểu field relation cha
                                                'parent_relation':False,#Model relation của field cha
                                                'model_id':False,#Model id
                                                'search_by':False,#Tìm kiếm field theo thuộc tính
                                                'index_column':index_column
                                                }
                                            })
                    tmp_splits = name_splits[:]
                    tmp_first = True
                    while(tmp_splits):
                        field_objs = ir_fields_pool.search([('name','=',tmp_splits[0]),('model_id','=',tmp_model_id)],limit=1)
                        if field_objs:
                            field = field_objs[0]
                            if tmp_first:
                                dict_field_tmp[field_name]['parent_name'] = field.name
                                dict_field_tmp[field_name]['parent_ttype'] = field.ttype
                                dict_field_tmp[field_name]['parent_relation'] = field.relation
                                if len(tmp_splits) > 1:
                                    tmp_first = False
                            dict_field_tmp[field_name]['name'] = field.name
                            dict_field_tmp[field_name]['ttype'] = field.ttype
                            dict_field_tmp[field_name]['relation'] = field.relation
                            dict_field_tmp[field_name]['model_id'] = field.model_id
                            if field.relation:
                                model_objs = ir_model_pool.search([('model','=',field.relation)],limit=1)
                                if model_objs:
                                    tmp_model_id = model_objs[0].id
                            if field.ttype in ('many2many','many2one') and len(tmp_splits) > 1:
                                dict_field_tmp[field_name]['search_by'] = tmp_splits[1]
                                parent_field = dict_field_tmp[field_name]['parent_ttype'] == 'one2many' and dict_field_tmp[field_name]['parent_ttype'] or ''
                                # Nếu có 2 cột many2many hoặc many2one trong file trở lên
                                name_field = field.name
                                if parent_field == 'one2many':
                                    name_field = '%s/%s' % (dict_field_tmp[field_name]['parent_name'], field.name)
                                if (name_field,parent_field) in list_field_m2m_m2o:
                                    list_m2m_m2o_error += len(list_m2m_m2o_error) and ', %s'%name_field or name_field
                                    is_error_when_check = True
                                else:
                                    list_field_m2m_m2o.append((name_field,parent_field))
                                break
                        else:
                            list_column_error += len(list_column_error) and ', %s'%field_name or field_name
                            is_error_when_check = True
                        tmp_splits.pop(0)
                    if dict_field_tmp[field_name]['parent_ttype'] in ('many2many','one2many'):
                        list_field_has_child.append(field_name)
                    if dict_field_tmp[field_name]['parent_ttype']=='many2many' or dict_field_tmp[field_name]['ttype']=='many2many':
                        m2m_export_mode = 'one_line'
                        if (not dict_field_tmp[field_name]['search_by']) or (dict_field_tmp[field_name]['search_by']=='id'):
                            m2m_export_mode = self_extend_pool.vks_get_many2many_export_mode(
                                                m_model_name=dict_field_tmp[field_name]['model_id'].model,
                                                m_field_name=dict_field_tmp[field_name]['name'])
                        else:
                            m2m_export_mode = 'many_line'
                        dict_field_tmp[field_name].update({'m2m_export_mode':m2m_export_mode})
                    elif dict_field_tmp[field_name]['ttype']=='binary':
                        tmp_check_image_field = self_extend_pool.vks_get_binary_field_export_param(
                                                    m_model_name=dict_field_tmp[field_name]['model_id'].model,
                                                    m_field_name=dict_field_tmp[field_name]['name'])
                        dict_field_tmp[field_name].update({'b_param':tmp_check_image_field})
                    elif dict_field_tmp[field_name]['ttype']=='json':
                        f_relation_pool = new_env[dict_field_tmp[field_name]['model_id'].model].sudo()
                        json_pool =  new_env[f_relation_pool.vks_get_json_model()].sudo()
                        json_search_f = f_relation_pool.vks_get_json_field_key()
                        json_search_d = new_env['ir.model.fields'].sudo().search([('model_id.model','=',json_pool._name),
                                                                           ('name','=',json_search_f)],limit=1).field_description
                        json_des = new_env['ir.model'].sudo().search([('model','=',json_pool._name)],limit=1).name
                        dict_field_tmp[field_name].update({'json_pool':json_pool,'json_search_f':json_search_f,
                                                           'json_search_d':json_search_d,'json_des':json_des})
                    index_column += 1
                if is_error_when_check:
                    message = ""
                    if len(list_m2m_m2o_error):
                        message=_("For field many2many, many2one : [%s] must have only a column for search value. Please check again!") % list_m2m_m2o_error
                    elif len(list_column_error):
                        message=_("Column define field : [%s] not found. Please check again!") % list_column_error
                    not_error = False
                    self_extend_pool.create_detail_import(import_id=record.id, row=0, message=message, status='fail')
                    record.write({'process_state': 'error'})
                    new_cr.commit()
                    return True
                #Duyệt từng dòng excel
                tmp_c_field_one2many_del_lst = []
                tmp_del_parent_row = False
                next_row = 0
                tmp_row_context = local_context.copy()
                for row in sheet._cell_values[from_row:]:
                    row_counter += 1
                    
                    #Nếu dòng hiện tại nhỏ hơn dòng cần xét kế tiếp thì bỏ qua (do ảnh hưởng bởi phần xóa bên dưới)
                    if row_counter < next_row:
                        continue
                    
                    #Ngược lại lấy số thứ tự của dòng kế tiếp
                    next_row = row_counter + 1 < tmp_total_s_row and row_counter + 1 or row_counter
                    
                    if current_row == 0:
                        current_row = row_counter + 1
                    #Kiểm tra required field
                    required_mess = self_extend_pool.check_required_field(name_fields[1:], row[1:], required_fields)
                    if required_mess and not is_child and sheet.cell(row_counter, 0).value:
                        self_extend_pool.create_detail_import(import_id=record.id, row=current_row, message=required_mess, status='fail')
                    else:
                        if not (is_child or sheet.cell(row_counter, 0).value):
                            line_message = _("Row %s in file must be child content of parent row has define id in columns A before!") % (row_counter + 1)
                            message += len(message) == 0 and line_message or VKS_NORMAL_NEW_LINE_CHAR + line_message
                            if sheet.cell(next_row, 0).value:
                                self_extend_pool.create_detail_import(import_id=record.id, row=current_row, message=message, status='fail')
                                message = ""
                                current_row = 0
                            continue
                        data_get = self_extend_pool.sudo().get_values_one_row(row=row[0:], name_fields=name_fields, model_id=model_id, 
                                                            model_create=model_create, sheet=sheet, row_index=row_counter, 
                                                            float_time_fields=float_time_fields, dict_field_tmp=dict_field_tmp, 
                                                            is_child=is_child, list_field_has_child=list_field_has_child)
                        vals_create = data_get.get('values', {})
                        if data_get['row_ctx']:
                            for ctx_key, ctx_vals in data_get['row_ctx'].items():
                                if ctx_key not in tmp_row_context:
                                    tmp_row_context[ctx_key] = ctx_vals
                                else:
                                    if isinstance(ctx_vals, dict):
                                        for sec_key, sec_vals in ctx_vals.items():
                                            tmp_row_context[ctx_key].update({sec_key:sec_vals})
                        
                        #Nếu cần xóa nguyên dòng đó
                        if IMP_DEL_ROW_KEY in vals_create:
                            tmp_del_parent_row = True
                        
                        #Cập nhật các dòng one2many vào vals chung
                        for o2m_key in data_get.get('o2m_keys', []):
                            if o2m_key in tmp_c_field_one2many_del_lst:
                                continue
                            
                            o2m_value = vals_create.get(o2m_key, {})
                            if not o2m_value:
                                vals_create[o2m_key] = []
                                continue
                            
                            tmp_chid_o2m_val_dict = o2m_value[0][2]
                            #Nếu ID là DELETE thì xóa toàn bộ các dòng one2many của bản ghi cha
                            if tmp_chid_o2m_val_dict.get('id','NOTID')==IMPT_DEL_ALL_ONE2MANY_ID:
                                tmp_c_field_one2many_del_lst.append(o2m_key)
                                if data_temp and (o2m_key in data_temp):
                                    data_temp[o2m_key] = [(5,0,0)]
                                else:
                                    vals_create[o2m_key] = [(5,0,0)]
                                    
                                continue
                            
                            #Ngược lại
                            tmp_del_child_row = tmp_chid_o2m_val_dict.pop(IMP_DEL_ROW_KEY,False)
                            is_empty_o2m = False
                            if not tmp_del_child_row:
                                is_empty_o2m = self_extend_pool.check_line_one2many_empty(sheet=sheet, one2many_key=o2m_key, 
                                                        list_fields=list_field_has_child, dict_field_tmp=dict_field_tmp, row_index=row_counter)
                            if is_empty_o2m:
                                vals_create[o2m_key] = []
                            else:
                                if not tmp_del_child_row:
                                    message_temp_child_o2m = self_extend_pool.check_required_for_special_field(field_name = o2m_key, 
                                                                vals_fields = tmp_chid_o2m_val_dict, required_special = o2m_required_fields, 
                                                                current_row = row_counter + 1, id_o2m_before = id_o2m_before)
                                    if message_temp_child_o2m:
                                        message_tmp = data_get.get('message', "")
                                        message_tmp += len(message_tmp) == 0 and message_temp_child_o2m or VKS_NORMAL_NEW_LINE_CHAR + message_temp_child_o2m
                                        data_get.update({'message': message_tmp})
                                        
                                m2m_in_o2m = data_get.get('m2m_in_o2m',{})
                                m2m_value = False
                                for field_name in tmp_chid_o2m_val_dict:
                                    if field_name in m2m_in_o2m:
                                        key_value = m2m_in_o2m[field_name]
                                        m2m_value = tmp_chid_o2m_val_dict[field_name]
                                        if str(m2m_value) == IMP_DELL_MANY2MANY:
                                            tmp_chid_o2m_val_dict[field_name] = [(6,0,[])]
                                        elif dict_field_tmp[key_value]['m2m_export_mode']=='many_line':
                                            if m2m_value:
                                                tmp_chid_o2m_val_dict[field_name] = [(6,0,[m2m_value])]
                                if 'id' in tmp_chid_o2m_val_dict:
                                    o2m_id = tmp_chid_o2m_val_dict.get('id')
                                    id_o2m_before = o2m_id
                                    tmp_chid_o2m_val_dict.pop('id')
                                    if data_temp:
                                        if o2m_key not in data_temp:
                                            data_temp.update({o2m_key : []})
                                        if tmp_del_child_row:
                                            data_temp[o2m_key].append((2,o2m_id,0))
                                        elif o2m_id == IMPT_NEW_ID_VALUE:
                                            data_temp[o2m_key].append(o2m_value[0])
                                        else:
                                            data_temp[o2m_key].append((1,o2m_id,tmp_chid_o2m_val_dict))
                                    else:
                                        if o2m_id != IMPT_NEW_ID_VALUE:
                                            if tmp_del_child_row:
                                                vals_create[o2m_key] = [(2,o2m_id,0)]
                                            else:
                                                vals_create[o2m_key] = [(1,o2m_id,tmp_chid_o2m_val_dict)]
                                elif id_o2m_before:
                                    message_tmp = data_get.get('message', "")
                                    for field_name in tmp_chid_o2m_val_dict:
                                        if field_name in m2m_in_o2m:
                                            key_value = m2m_in_o2m[field_name]
                                            if dict_field_tmp[key_value]['m2m_export_mode']=='one_line' and tmp_chid_o2m_val_dict[field_name][0][2]:
                                                m_tmp = _('Row %s: Field %s Can not set value in line not have id for one2many') % (row_counter+1,key_value)
                                                message_tmp += len(message_tmp) == 0 and m_tmp or VKS_NORMAL_NEW_LINE_CHAR + m_tmp
                                            else:
                                                value_m2m = tmp_chid_o2m_val_dict[field_name][0][2][0]
                                                if field_name not in data_temp[o2m_key][-1][2]:
                                                    data_temp[o2m_key][-1][2][field_name] = [(6,0,[])]
                                                data_temp[o2m_key][-1][2][field_name][0][2].append(value_m2m)
                                        else:
                                            m_tmp = _('Row %s: Field %s/%s Can not set value in line not have id for one2many') % (row_counter+1,o2m_key,field_name)
                                            message_tmp += len(message_tmp) == 0 and m_tmp or VKS_NORMAL_NEW_LINE_CHAR + m_tmp
                                    data_get.update({'message': message_tmp})
                        #Cập nhật ids cho many2many vào vals (trường hợp không tìm kiếm theo field id)
                        m2m_value = False
                        for m2m_key in data_get.get('m2m_keys', []):
                            m2m_value = vals_create.get(m2m_key,False)
                            if m2m_value:
                                if str(m2m_value)==IMP_DELL_MANY2MANY:
                                    m2m_value = []
                                if data_temp:
                                    if m2m_key not in data_temp:
                                        data_temp.update({m2m_key : [(6,0,[])]})
                                    if m2m_value:
                                        data_temp[m2m_key][0][2].append(m2m_value)
                                else:
                                    if isinstance(m2m_value,list):
                                        vals_create[m2m_key] = [(6,0,m2m_value)]
                                    else:
                                        vals_create[m2m_key] = [(6,0,[m2m_value])]
                        #Kiểm tra dòng tiếp theo có id hay không - Để xác định là dòng con hay dòng cha
                        if not sheet.cell(next_row, 0).value:
                            if not is_child:
                                is_child = True
                                data_temp = vals_create
                                current_row = current_row
                                success = data_get.get('success', False)
                            if row_counter + 1 == tmp_total_s_row:
                                is_child = False
                                id_o2m_before = False
                                next_row = -1
                        else:
                            is_child = False
                            id_o2m_before = False
                            if not data_temp:
                                data_temp = vals_create
                                success = data_get.get('success', False)
                        if data_get.get('message', "") != "":
                            message += len(message) == 0 and data_get.get('message', "") or VKS_NORMAL_NEW_LINE_CHAR + data_get.get('message', "")
                            success = False
                        if (not is_child) or tmp_del_parent_row:
                            if success:
                                try:
                                    if 'id' in data_temp:
                                        data_id = data_temp.pop('id')
                                        if tmp_del_parent_row:
                                            #Tìm xem dòng nào trong file excel sẽ là dòng chứa ID tiếp theo
                                            if next_row > 0:
                                                while (next_row < tmp_total_s_row):
                                                    if sheet.cell(next_row, 0).value:
                                                        is_child = False
                                                        break
                                                    next_row +=1
                                            #Xóa bản ghi
                                            create_pool.with_context(tmp_row_context).browse(data_id).unlink()
                                            new_cr.commit()
                                            self_extend_pool.create_detail_import(import_id=record.id, row=current_row, type='delete')
                                        elif data_id != IMPT_NEW_ID_VALUE:
                                            #Cập nhật bản ghi
                                            create_pool.with_context(tmp_row_context).browse(data_id).write(data_temp)
                                            new_cr.commit()
                                            self_extend_pool.create_detail_import(import_id=record.id, row=current_row, type='write')
                                        else:
                                            #Tạo mới bản ghi
                                            create_pool.with_context(tmp_row_context).create(data_temp)
                                            new_cr.commit()
                                            self_extend_pool.create_detail_import(import_id=record.id, row=current_row, type='create')
                                    success_row += 1
                                except Exception as e:
                                    new_cr.rollback()
                                    not_error = False
                                    mess = False
                                    try: 
                                        mess = (e.message or e.value)
                                    except Exception as ex:
                                        mess = str(e)
                                    mess = mess.encode('utf-8').decode('utf-8')
                                    self_extend_pool.create_detail_import(import_id=record.id, row=current_row, message=mess, status='fail')
                            else:
                                not_error = False
                                self_extend_pool.create_detail_import(import_id=record.id, row=current_row, message=message, status='fail')
                                
                    if next_row < 0:
                        current_row = tmp_total_s_row
                        
                    record.write({'current_row': current_row,'success_row': success_row})
                    new_cr.commit()
                    if not is_child:
                        tmp_c_field_one2many_del_lst = []
                        tmp_del_parent_row = False
                        data_temp = {}
                        tmp_row_context = local_context.copy()
                        message = ""
                        current_row = 0
            if not_error:
                record.write({'process_state': 'done'})
            else:
                record.write({'process_state': 'error'})
            new_cr.commit()
            
            #Gửi mail thông báo
            template_obj = new_env['common.method'].get_special_mail_template_by_xml_id(
                            str_xml_id='vks_import_excel.email_template_import_data')
            url = menu_pool.get_access_link(for_view_action=record.get_formview_action())
            act_id = self_extend_pool.get_action_import()
            if act_id:
                base_url = "%s&action=%s"%(url,act_id[0])  
            else:
                base_url = url
            
            mail_context = local_context.copy() 
            mail_context.update({
                'email_template_obj' : template_obj,
                'base_url': base_url,
                'send_email_for_current_user': True,
                'system_user_name': _('System')
            })
            
            tmp_mail_id = template_obj.with_context(mail_context).sudo().send_mail(record.id, force_send=True, raise_exception=False)
            mail_message_obj = new_env['mail.mail'].sudo().browse(tmp_mail_id).mail_message_id
            
            #Xây dựng thông điệp ở dạng chat để thông báo
            new_env['mail.message'].vks_make_messeage_notify_chat(
                    partner_need_send_inbox_ids=[record.sudo().create_uid.partner_id.id],
                    mail_message_obj=mail_message_obj,make_none_model=True)
            
            new_cr.commit()
            
        except Exception as e:
            new_cr.rollback()
            mess = False
            try: 
                mess = (e.message or e.value)
            except Exception as ex:
                mess = str(e)
            mess = mess.encode('utf-8').decode('utf-8')
            self_extend_pool.create_detail_import(import_id=record.id, row=current_row, message=mess, status='fail')
            #Nếu xảy ra Exception buộc phải sql query để tránh tính toán lại các field function
                #khiến không thể chuyển trạng thái import
            str_sql_query_tmp = """
Update import_data set process_state = 'error', write_uid = %s, write_date = '%s' where id = %s 
""" % (self._uid, datetime.utcnow(), record.id)
            new_cr.execute(str_sql_query_tmp)
            new_cr.commit()
        finally:
            new_cr.close()
        return True
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm dùng cho hàm khác
    @api.model
    def get_action_import(self):
        dummy, search_view_id = self.env['ir.model.data'].sudo().get_object_reference('vks_import_excel', "view_import_data_filter")
        act_objs = self.env['ir.actions.act_window'].sudo().search([('search_view_id', '=', search_view_id)],limit=1)
        return act_objs and act_objs[0].id or False
    
    #Thêm bởi Tuấn - 06/11/2023 - Hàm đọc file excel gọi từ view
    def act_call_read_excel_thread(self):
        vks_context = dict(self._context) or {}
        
        manage_obj_pool = self.env['manage.object.import']
        ir_field_pool = self.env['ir.model.fields'].sudo()
        ir_model_pool = self.env['ir.model'].sudo()
        
        try:
            refrence_template = self.env['ir.model.data'].get_object_reference('vks_import_excel', 'email_template_import_data')
        except Exception as e:
            raise UserError(_('Could not find email template!'))
        
        for data in self:
            if not data.model_id:
                raise UserError(_('Please select object to import'))
            if not data.file_import:
                raise UserError(_('Please select file to import.'))
            if not data.create_uid.partner_id:
                raise UserError(_('The creator of this record does not have related partner.'))
            elif not data.create_uid.partner_id.email or not len(data.create_uid.partner_id.email.strip()):
                raise UserError(_('The related partner of the creator of this record does not have email.'))
            base_data = base64.decodebytes(data.file_import)
            row_book = False
            try:
                row_book = xlrd.open_workbook(file_contents=base_data)
            except:
                raise UserError(_('Format error. Please choose a file with format type is xlsx or xls.'))
            #Không cho phép import nếu số lượng sheet của file excel > 1 để đảm bảo dữ liệu chính xác hơn cũng như giảm dung lượng lưu trữ.
            sheet = False
            if len(row_book.sheet_names())>1:
                raise UserError(_('Please using excel file which include only one sheet to import data!'))
            else:
                sheet = row_book.sheet_by_index(0)
            if sheet.ncols == 0:
                raise UserError(_('Please check file Import. File is Empty!'))
            
            #Lấy ra các field required được define trong file py của object
            required_objs = ir_field_pool.search([('model_id','=',data.model_id.id),('required','=',True)])
            required_fields = [x.name for x in required_objs]
            #Lấy ra các field required của đối tượng relation của field one2many được define trong file py của object
            o2m_required_fields = {}
            o2m_field_objs = ir_field_pool.search([('model_id','=',data.model_id.id),('ttype','=','one2many')])
            for o2m_field in o2m_field_objs:
                if o2m_field.name not in o2m_required_fields:
                    o2m_required_fields.update({o2m_field.name : []})
                for o2m_key in o2m_required_fields.keys():
                    if o2m_key == o2m_field.name:
                        model_objs = ir_model_pool.search([('model','=',o2m_field.relation)], limit=1)
                        if model_objs:
                            field_objs = ir_field_pool.search([('model_id','=',model_objs[0].id),('required','=',True)])
                            list_required = [o2m_key +'/'+ x.name for x in field_objs]
                            o2m_required_fields[o2m_key] = list(set(o2m_required_fields[o2m_key] + list_required))
                        break
            o2m_required_fields_tmp = o2m_required_fields.copy()
            for x in o2m_required_fields_tmp.keys():
                if not o2m_required_fields_tmp[x]:
                    o2m_required_fields.pop(x, None)
            float_time_fields = []
             
            #Tìm cấu hình của người dùng cho field import của object được chọn import (nếu có)
            manage_objs = manage_obj_pool.search([('model_id','=',data.model_id.id)], limit=1)
            if manage_objs:
                manage_obj = manage_objs[0]
                required_fields_tmp = []
                #Lấy ra các dòng là field required của object import được người dùng cấu hình
                for child_f in manage_obj.required_fields:
                    required_fields_tmp.append(child_f.name)
                required_fields = list(set(required_fields + required_fields_tmp))
                #Lấy ra các dòng là field có widget float time của object import được người dùng cấu hình
                float_time_fields = []
                for child_f in manage_obj.float_time_fields:
                    float_time_fields.append(child_f.name)
                    
            #Gọi và bắt đầu thread
            m_extend_context = vks_context.copy()
            #Cập nhật url cho việc tạo link trong mail hoặc render template
            if 'verp_base_real_url' not in m_extend_context:
                m_extend_context.update({'verp_base_real_url':self.env['common.method'].get_vks_base_url()['vks_root_url']})

            tmp_record_thread = threading.Thread(target=getattr(data.with_context(m_extend_context), 'thread_general_import_common'), 
                                    kwargs= {
                                      'sheet' : sheet, 
                                      'required_fields':required_fields, 
                                      'o2m_required_fields':o2m_required_fields, 
                                      'float_time_fields':float_time_fields
                                    },
                                    name = 'import_data_thread_general_import_common_%s' % (data.id)
                             )
            tmp_record_thread.start()
            time.sleep(1)
        return True

class ImportDataStatus(models.Model):
    _name = 'import.data.status'
    _description = "Ket qua nhap du lieu"
    _order = 'status asc, row_number desc'
 
    status = fields.Selection(VKS_STATUS_PROCESS_COMMON, string='Status',readonly=True)
    type = fields.Selection([('create','Create'),('write','Write'),('delete','Delete'),('exc','Exception')], string='Type',readonly=True)
    import_id = fields.Many2one('import.data', string='Import ID', ondelete='cascade',readonly=True)
    row_number = fields.Integer(string='Row',readonly=True)
    id_data = fields.Integer(string='Ref record id',readonly=True)
    message = fields.Text(string='Message',readonly=True)
    