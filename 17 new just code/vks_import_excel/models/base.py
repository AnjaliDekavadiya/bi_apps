# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from .common_const import *
from odoo.exceptions import UserError, ValidationError
from odoo import tools, SUPERUSER_ID
from urllib.parse import urlencode, urljoin
from datetime import datetime
import datetime as vks_dt_extend
import re
from operator import attrgetter,itemgetter

class IrModelData(models.Model):
    _inherit = 'ir.model.data'
    
    #Thêm bởi Tuấn - 05/10/2023
    @api.model
    @tools.ormcache('xmlid')
    def xmlid_lookup(self, xmlid):
        """Low level xmlid lookup
        Return (id, res_model, res_id) or raise ValueError if not found
        """
        module, name = xmlid.split('.', 1)
        xid = self.sudo().search([('module', '=', module), ('name', '=', name)])
        if not xid:
            raise ValueError('External ID not found in the system: %s' % xmlid)
        # the sql constraints ensure us we have only one result
        res = xid.read(['model', 'res_id'])[0]
        if not res['res_id']:
            raise ValueError('External ID not found in the system: %s' % xmlid)
        return res['id'], res['model'], res['res_id']
    
    #Thêm bởi Tuấn - 05/10/2023
    @api.model
    def xmlid_to_res_model_res_id(self, xmlid, raise_if_not_found=False):
        """ Return (res_model, res_id)"""
        try:
            return self.xmlid_lookup(xmlid)[1:3]
        except ValueError:
            if raise_if_not_found:
                raise
            return (False, False)

    #Thêm bởi Tuấn - 05/10/2023
    @api.model
    def xmlid_to_object(self, xmlid, raise_if_not_found=False):
        """ Return a Model object, or ``None`` if ``raise_if_not_found`` is 
        set
        """
        t = self.xmlid_to_res_model_res_id(xmlid, raise_if_not_found)
        res_model, res_id = t

        if res_model and res_id:
            record = self.env[res_model].browse(res_id)
            if record.exists():
                return record
            if raise_if_not_found:
                raise ValueError('No record found for unique ID %s. It may have been deleted.' % (xmlid))
        return None

    #Thêm bởi Tuấn - 05/10/2023
    @api.model
    def get_object_reference(self, module, xml_id):
        return self.xmlid_lookup("%s.%s" % (module, xml_id))[1:3]
    
    #Thêm bởi Tuấn - 05/10/2023
    @api.model
    def get_object(self, module, xml_id):
        """ Returns a browsable record for the given module name and xml_id.
            If not found, raise a ValueError or return None, depending
            on the value of `raise_exception`.
        """
        return self.xmlid_to_object("%s.%s" % (module, xml_id), raise_if_not_found=True)

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy mô tả của 1 field theo ngôn ngữ
    @api.model
    def get_description_of_field_in_lang(self,field_obj,lang):
        res = False
        try:
            #Lấy ra base_field
            col_infor = self.env[field_obj.model]._fields[field_obj.name].base_field
            #Tìm giá trị dịch cho field (phải dùng cách này để phòng cả trường hợp related field)
            str_field_name = "%s,%s" % (col_infor.model_name, col_infor.name)
            #Tìm giá trị dịch của  field đó
            res = self.env['ir.translation']._get_source(name=str_field_name, types='field', lang=lang)
            #Nếu không có giá trị dịch thì lấy field_description
            if not res:
                res = field_obj.field_description
        except Exception as e:
            res = field_obj.field_description
        return res
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của odoo
    def name_get(self):
        vks_context = dict(self._context) or {}
        current_lang = vks_context.get('lang','en_US')
        res = []
        for record in self:
            name = record.get_description_of_field_in_lang(field_obj=record, lang=current_lang)
            res.append((record.id, name))
        return res
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của odoo
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        domain = args + ['|',('field_description', operator, name), ('name', operator, name)]
        return self.search(domain, limit=limit).name_get()

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm get link view 1 record cho form view
    @api.model
    def get_access_link(self, for_view_action):
        """
        paramaters:
            1. for_view_action :  self.get_formview_action(cr, uid, id, context)
        Output:
        Link with structure:
        hostname/web?db=database#id= &model= &view_type= 
        """
        vks_context = dict(self._context) or {}
        result_url = ''
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        db_name = self._cr.dbname
        res_id = for_view_action.get('res_id')
        res_model = for_view_action.get('res_model')
        #Nếu muốn trả về dạng click vào link không bị mất menu
        if vks_context.get('keep_all_menu',False):
            tmp_menu_id = vks_context.get('special_menu_id',False)
            if tmp_menu_id:
                tmp_menu_obj = self.browse(tmp_menu_id)
                result_url = """%s/web?db=%s#id=%s&view_type=form&model=%s&menu_id=%s&action=%s""" % (base_url,
                                                db_name,res_id,res_model,tmp_menu_obj.id,tmp_menu_obj.action.id)
            else:
                result_url = """%s/web?db=%s#action=mail.action_mail_redirect&model=%s&res_id=%s""" % (base_url,
                                                                        db_name,res_model,res_id)
        #Nếu muốn trả về dạng click vào link mất menu theo mặc định của Odoo
        else:
            query = {'db': db_name}
            fragment = {}
            fragment.update(id=res_id,view_type=for_view_action.get('view_type'),model=res_model)
            result_url = urljoin(base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment)))
        return result_url

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    #Thêm bởi Tuấn - 16/10/2023 - Hàm kiểm tra dữ liệu trước khi lưu
    @api.model
    def process_before_save(self,vals,data_obj):
        try:
            if 'datas' in vals:
                vks_context = dict(self._context) or {}
                tmp_res_model = vals.get('res_model', data_obj and data_obj.res_model or self._name)
                if tmp_res_model in vks_context:
                    tmp_name = 'datas'
                    if tmp_res_model!=self._name:
                        tmp_name = vals.get('name', data_obj and data_obj.name or 'unknow')
                    vals['url'] = vks_context[tmp_res_model][tmp_name]
        except Exception as e:
            pass
        return vals
    
    #Thêm bởi Tuấn - 16/10/2023 - Ghi đè hàm của Odoo
    @api.model
    def create(self,vals):
        vals = self.process_before_save(vals=vals,data_obj=False)
        return super(IrAttachment, self).create(vals)
    
    #Thêm bởi Tuấn - 16/10/2023 - Ghi đè hàm của Odoo
    def write(self,vals):
        for data in self:
            #Chuẩn hóa dữ liệu
            tmp_vals = vals.copy()
            tmp_vals = self.process_before_save(vals=tmp_vals,data_obj=data)
            super(IrAttachment,data).write(tmp_vals) 
            
        return True 
    
class IrExports( models.Model ):
    _name = 'ir.exports'
    _inherit = ['ir.exports', 'mail.thread.main.attachment']

    name = fields.Char(translate=True,tracking=True)
    related_object = fields.Many2one('ir.model', string='Model',help='Specify the object to export data',tracking=True)
    related_filter = fields.Many2one('ir.filters', string='Filter',
        help='Specify a filter to limit the number of lines of output data',tracking=True)
    file_name = fields.Char(string='Filename', size=255)
    color = fields.Integer( string='Color Index' )
    attachment_date = fields.Datetime(related='message_main_attachment_id.create_date', string="Last export date",readonly=True)
    export_fields = fields.One2many(order='sequence,heading,name')
    notes = fields.Text('Notes',tracking=True) 
    privacy = fields.Selection([('owner','Owner'),
                                ('followers','Followers'),
                                ('groups','Designated groups'),
                                ('none','Public')], 
                                default='owner', string='Security',tracking=True,required=True)
    privacy_groups = fields.Many2many(comodel_name='res.groups',relation='ir_exports_groups_rel',column1='exp_id',column2='group_id',
                                      string='Groups are allowed to access', tracking=True) 
    
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm gọi khi onchange related_object
    @api.onchange('related_object')
    def onchange_related_object(self):
        res ={}
        if self.related_object:
            res['resource'] = self.related_object.model
        else:
            res['resource'] = ''
        res['export_fields'] = []
        res['related_filter'] = False
        return {'value': res}
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    @api.model
    def create(self,vals):
        vals = self.process_before_save(vals=vals,data_obj=False)
        new_obj = super(IrExports,self).create(vals)
        return new_obj
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    def write(self, vals):
        for data in self:
            tmp_vals = vals.copy()
            tmp_vals = self.process_before_save(vals=tmp_vals,data_obj=data)
            super(IrExports, data).write(tmp_vals)
        return True
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý dữ liệu trước khi lưu
    @api.model
    def process_before_save(self,vals,data_obj):
        #Luôn đảm bảo resource và related_object thống nhất với nhau
        if vals.get('resource',False):
            tmp_related_object = self.env['ir.model'].sudo().search([('model','=',vals['resource'])],limit=1)[0]
            vals.update({'related_object':tmp_related_object.id})
        elif vals.get('related_object',False):
            tmp_related_object = self.env['ir.model'].sudo().browse(vals['related_object'])
            vals.update({'resource':tmp_related_object.model})
        
        return vals
    
    #Thêm bởi Tuấn - 13/10/2023 - Tách đoạn code lấy các style đặc biệt để export excel
    @api.model
    def vks_get_export_special_styles(self,prop_style_common,fields_des_dict_lst,is_hide_technical_row,
            s_export_obj,workbook,worksheet):
        
        header_style = workbook.add_format(prop_style_common)
        header_style.set_bold(True)
        header_style.set_bg_color('#ffffcc')
        header_style.set_text_wrap(False)
        
        header_description_style = workbook.add_format(prop_style_common)
        header_description_style.set_bold(True)
        header_description_style.set_bg_color('#ccffff')
        header_description_style.set_text_wrap(False)
        
        header_note_style = workbook.add_format(prop_style_common)
        header_note_style.set_bold(True)
        header_note_style.set_bg_color('#ff8080')
        
        base_style = workbook.add_format(prop_style_common)
        
        date_style = workbook.add_format(prop_style_common)
        date_style.set_num_format('YYYY-MM-DD') 
        
        datetime_style = workbook.add_format(prop_style_common)
        datetime_style.set_num_format('YYYY-MM-DD HH:mm:SS') 
        
        time_style = workbook.add_format(prop_style_common)
        time_style.set_num_format('hh:mm') 
        
        return {'fields_des_dict_lst':fields_des_dict_lst,'header_style':header_style,
                'header_description_style':header_description_style,'header_note_style':header_note_style, 
                'base_style': base_style,'date_style':date_style,
                'datetime_style':datetime_style,'time_style':time_style
                }
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm ghi dữ liệu excel đối với chức năng xuất dữ liệu thông thường
    def from_data(self,fields,rows,fields_des_dict_lst=[],is_hide_technical_row=False,
        att_file_name=False,res_id=-1,s_export_obj=False):
        
        vks_context = dict(self._context) or {}
        common_method_pool = self.env['common.method']
        io_stream = False
        workbook = vks_context.get('special_workbook',False)
        if not workbook:
            tmp_wookbook_data =  common_method_pool.make_new_wookbook_common()
            io_stream = tmp_wookbook_data['io_stream']
            workbook = tmp_wookbook_data['workbook_obj']
            
        worksheet = workbook.add_worksheet(vks_context.get('special_worksheet_name','Sheet 1'))
        
        #----------------------------------------Define Style-----------------------------------------------------
        res_vals = self.vks_get_export_special_styles(prop_style_common={'indent':1,'border': 1,'text_wrap' :1,
                                                             'align':'left','valign':'vcenter',
                                                             'font_name':'Arial','font_size':10},
                            fields_des_dict_lst=fields_des_dict_lst,
                            is_hide_technical_row=is_hide_technical_row,
                            s_export_obj=s_export_obj, workbook=workbook, worksheet=worksheet)
        
        fields_des_dict_lst = res_vals.pop('fields_des_dict_lst')
        
        tmp_column_style = False
        tmp_column_infors = False
        tmp_has_note_row = False
        tmp_has_heading_row = False
        tmp_column_type = False
        float_time_column_index = []
        empty_if_false_index = []
        tmp_ex_formula_dict = {}
        
        
        #----------------------------------------Insert Header--------------------------------------------------
        for i, fieldname in enumerate(fields):
            tmp_column_infors = fields_des_dict_lst and fields_des_dict_lst[i] or {}
            tmp_column_style = tmp_column_infors.get('ex_style', res_vals['base_style'])
            tmp_column_type = tmp_column_infors.get('type','')
            if tmp_column_type=='time':
                float_time_column_index.append(i)
                tmp_column_style = res_vals['time_style']
            elif tmp_column_type=='date':
                tmp_column_style = res_vals['date_style']
            elif tmp_column_type=='datetime':
                tmp_column_style = res_vals['datetime_style']
            else:
                if 'ex_formula' in tmp_column_infors:
                    tmp_ex_formula_dict.update({str(i):tmp_column_infors['ex_formula']})
                
            worksheet.set_column(i,i,tmp_column_infors.get('ex_width',VKS_EXPORT_EXCEL_CELL_WIDTH),tmp_column_style)
            
            worksheet.write(0, i, fieldname, res_vals['header_style'])
            
            if 'heading' in tmp_column_infors:
                worksheet.write(1, i, tmp_column_infors['heading'], res_vals['header_description_style'])
                if not tmp_has_heading_row:
                    tmp_has_heading_row = True
                    
            if 'note' in tmp_column_infors:
                worksheet.write(2, i, tmp_column_infors['note'], res_vals['header_note_style'])
                if not tmp_has_note_row:
                    tmp_has_note_row = True
            
            if tmp_column_infors.get('empty_if_false',True):
                empty_if_false_index.append(i)
            
        #Nếu ẩn row chứa tên kỹ thuật (hay nói cách khác là chỉ xuất dữ liệu để xem mà không import lại)
        if is_hide_technical_row:
            worksheet.set_row(0,0)
        
        #----------------------------------------Insert Data--------------------------------------------------
        
        toltal_row_for_header = 1
        freeze_row_index = 1
        
        if tmp_has_note_row:
            toltal_row_for_header = 3
            freeze_row_index = 3
        
        elif tmp_has_heading_row:
            toltal_row_for_header = 2
            freeze_row_index = 2
        
        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                #Nếu cell_value có giá trị false và cột này được quy định chuyển giá trị False thành chuỗi rỗng
                if str(cell_value) == 'False' and cell_index in empty_if_false_index:
                    cell_value =''
                #Nếu là kiểu float time
                elif cell_value and cell_index in float_time_column_index:
                    cell_value = cell_value/24
                #Nếu là kiểu string
                elif isinstance(cell_value, str):
                    cell_value = re.sub( "\r", " ", cell_value )
                #Nếu là kiểu datetime
                elif isinstance(cell_value, datetime):
                    #Nếu chỉ xuất dữ liệu để xem thì chuyển đổi giá trị về múi giờ của người dùng hiện tại
                    if is_hide_technical_row:
                        cell_value = common_method_pool.convert_str_datetime_between_utc_and_user_tz(
                                                str_value=str(cell_value),convert_type=0,remove_tz_infor=True)
                #Nếu là kiểu bytes
                elif isinstance(cell_value, bytes):
                    if len(cell_value) > 32767:
                        cell_value = 'The content of this cell is too long for an XLSX file (more than 32767 characters)'
                    else:
                        cell_value = cell_value.decode('utf-8')
                else:
                    if tmp_ex_formula_dict and str(cell_index) in tmp_ex_formula_dict:
                        cell_value = eval(tmp_ex_formula_dict[str(cell_index)])
                        
                worksheet.write(row_index + toltal_row_for_header, cell_index, cell_value)
        
        #---------------------------------------Freeze Pane-------------------------------------------------
        
        freeze_column_index = 1
        
        total_column = len(fields)
        if total_column <= 2:
            freeze_column_index = 1
        else:
            freeze_column_index = 2    
                
        worksheet.freeze_panes(freeze_row_index, freeze_column_index)
        
        #---------------------------------------------------End----------------------------------------------
        
       
        res_vals.update({'workbook_obj':workbook,
                    'io_stream':io_stream,
                    'toltal_row_for_header':toltal_row_for_header,
                    'last_row_index':toltal_row_for_header + (len(rows) or 0)
                    })
        
        #Nếu cần tạo file đính kèm
        if att_file_name:
            res_vals.update({'att_obj':common_method_pool.make_binary_data_from_wookbook(workbook_obj=workbook,
                                        io_stream=io_stream, need_make_att=True,
                                        download_file_name=att_file_name,res_id=res_id)})
        return res_vals
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm nối ghi chú mặc định của hệ thống và ghi chú do người dùng nhập
    @api.model
    def merge_default_note_and_user_note(self,default_note,user_note):
        if default_note and default_note!='':
            if not user_note or user_note.lower()=='false':
                return default_note
            else:
                if not default_note.startswith('-'):
                    default_note = '- %s' % default_note
                if user_note.startswith('-'):
                    return '%s\n%s' % (default_note,user_note)
                else:
                    return '%s\n- %s' % (default_note,user_note)
        return user_note or ''
    
    #Thêm bởi Tuấn - 02/10/2023 - Tách code phần tạo điều kiện sắp xếp thành hàm dùng chung
    @api.model
    def vks_standardized_sort_cond(self,sort_condition,src_sort_type):
        #Ý nghĩa tham số đầu vào:
            #sort_condition: điều kiện sắp xếp
            #src_sort_type: nguồn gọi để biết cách chuẩn hóa
        
        #Nếu có điều kiện sắp xếp 
        str_sort_condition = False
        if sort_condition:
            sort_type = '-'
            str_sort_condition = ''
            #Theo debug thì điều kiện sắp xếp của Odoo là kiểu mảng và theo quy luật LIFO nếu gọi trực tiếp từ view
            if src_sort_type=='view':
                for child_cond in sort_condition:
                    if child_cond.get('asc',False)==False:
                        sort_type = 'desc'
                    else:
                        sort_type = 'asc'
                    str_sort_condition += '%s %s,' % (child_cond['name'], sort_type)
            #Ngược lại nếu gọi từ filter thì theo Odoo cũng định nghĩa kiểu mảng nhưng cách ký hiệu tăng giảm sẽ khác
            elif src_sort_type=='filter':
                str_tmp_real_field = False
                tmp_arr_cond = False
                for child_cond in sort_condition:
                    tmp_arr_cond = child_cond.split(' ');
                    str_tmp_real_field = tmp_arr_cond[0];
                    if len(tmp_arr_cond)==1:
                        sort_type = 'asc'
                    else:
                        sort_type = tmp_arr_cond[1];
                    str_sort_condition += '%s %s,' % (str_tmp_real_field, sort_type)
                
        #Loại bỏ dấu phẩy cuối cùng trong điều kiện sắp xếp nếu có
        if str_sort_condition and str_sort_condition!='':
            str_sort_condition = str_sort_condition[:-1]
        else:
            str_sort_condition = False
            
        return str_sort_condition
    
    #Thêm bởi Tuấn - 13/10/2023 - Hàm kiểm tra có bỏ qua field khi import hay không
    @api.model
    def vks_check_skip_import_field(self,child_field,by_import_template,exist_field_names):
        tmp_skip = False
        try:
            if by_import_template:
                tmp_f_name = child_field.name
                if tmp_f_name in exist_field_names:
                    if tmp_f_name=='id' or tmp_f_name.endswith('/id'):
                        tmp_skip = True
        except:
            tmp_skip = False
            
        return tmp_skip
        
    #Thêm bởi Tuấn - 31/10/2023 - Hàm tạo tên file export nếu không chỉ định tên cụ thể
    @api.model
    def vks_default_export_excel_name(self,export_obj):
        return '%s (%s)' % (export_obj.name, export_obj.resource)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm export dữ liệu dùng chung
    def export_with_domain(self,by_import_template=False, include_data=True,
                special_domain=None,str_sort_condition=False,
                custom_file_name=False,res_id=-1):
        #Ý nghĩa tham số đầu vào:
            #by_import_template : có export theo template import hay không
            #include_data: nếu false là chỉ xuất template import
            #special_domain: nếu không chỉ định sẽ lấy domain đã thiết lập trên template xuất dữ liệu tương ứng
            #str_sort_condition: điều kiện sort (nếu có)
            #custom_file_name : tên file download (nếu không chỉ định sẽ lấy theo tên model export)
            #res_id :ý nghĩa tương tự hàm from_data
        
        try:
            models.VKS_STR_SPLIT_MANY2MANY_VALUES = ',' 
        except Exception as e:
            pass
            
        tmp_split_many2many_char = VKS_STR_SPLIT_MANY2MANY_VALUES
        tmp_import_note_for_many2many_field = tools.ustr(_('Enter values separated by %s. Example Value 1%sValue 2%sValue 3') % (
                                                tmp_split_many2many_char,tmp_split_many2many_char,tmp_split_many2many_char))
        vks_context = dict(self._context) or {}
        common_method_pool = self.env['common.method']
        local_context = vks_context.copy()
        local_context.update({'vks_call_from_export':True})
        if self.export_fields :
            field_pool = self.env['ir.model.fields']
            field_import_pool = False
            try:
                field_import_pool = self.env['manage.field.import'].sudo()
            except:
                field_import_pool = False
            field_names = []
            fields_des_dict_lst = []
            tmp_fields_infors = False
            tmp_field_type = False
            default_id_column_note = tools.ustr(_("""- If you want to create a new record, write the new value in this column.
- If you want to update data for an existing record, keep the same value as the output file.
- If you want to delete an existing record, add the word DEL_ROW at the end of the output file's value."""))
            
            rexport_fields_sorted = self.export_fields.sorted(key=attrgetter('sequence','id'))
            
            #---------Xây dựng định nghĩa cho các field để định dạng excel, loại bỏ các field trùng lặp và thêm các ghi chú mặc định----------
            
            #Nếu xuất dữ liệu theo template import thì bổ sung cột id vào đầu tiên nếu model là dạng table
            if by_import_template and self.env[self.resource]._auto:
                import_note_for_main_id_field = self.merge_default_note_and_user_note(
                        default_note=tools.ustr(_('The area to import data will be calculated from the 4th line of this file')), 
                        user_note=default_id_column_note)
                
                field_names.insert(0,'id')
                tmp_fields_infors = {'name':'id','heading':'ID','type': 'integer',
                             'empty_if_false':False,'note':import_note_for_main_id_field}
                fields_des_dict_lst.insert(0,tmp_fields_infors)
            
            #Định nghĩa cho các field còn lại      
            for child_field in rexport_fields_sorted:
                #Loại bỏ các cột trùng lặp nếu là xuất dữ liệu theo biểu mẫu import
                if self.vks_check_skip_import_field(child_field=child_field,by_import_template=by_import_template,
                                                    exist_field_names=field_names):
                    continue 
                
                tmp_fields_infors = False
                tmp_field_type = 'char'
                
                #Khởi gán giá trị ghi chú mặc định = ''
                tmp_default_note_to_add = ''
                #Tách column name bởi dấu /
                s_field_name = child_field.name
                s_field_heading = child_field.heading
                tmp_fields_arr = s_field_name.split('/')
                #Nếu column là cột id (tên column được đặt theo cú pháp .../id)
                if len(tmp_fields_arr) > 1 and tmp_fields_arr[len(tmp_fields_arr)-1]=='id':
                    tmp_field_type = 'integer'
                    #Khởi gán tên model = tên model của class export
                    tmp_current_model_name = self.resource
                    #Khởi gán kiểu dữ liệu của column = False
                    tmp_current_field_type = False
                    for child_field_name in tmp_fields_arr:
                        if not tmp_current_model_name or child_field_name == 'id':
                            break
                        #Tìm field tương ứng
                        tmp_field_obj = field_pool.search([('model_id.model','=',tmp_current_model_name),
                                                           ('name','=',child_field_name)],limit=1)
                        #Gán lại model, type, required cho column đó
                        tmp_current_model_name = tmp_field_obj.relation
                        tmp_current_field_type = tmp_field_obj.ttype
                        
                    #Nếu field đó là kiểu many2many
                    if by_import_template:
                        if tmp_current_field_type == 'many2many':
                            tmp_display_mode = self.vks_get_many2many_export_mode(m_model_name=tmp_field_obj.model_id.model,
                                                                            m_field_name=tmp_field_obj.name)
                            if tmp_display_mode=='one_line':
                                tmp_default_note_to_add = tmp_import_note_for_many2many_field
                        else:
                            tmp_default_note_to_add = default_id_column_note
                else:
                    try:
                        tmp_float_time_ids = field_import_pool.search(
                                                [('name','=',s_field_name),
                                                 ('manage_id.model_id','=',self.related_object.id),
                                                 ('type','=','float_time')],limit=1)
                        #Nếu field có dạng float time
                        if tmp_float_time_ids:
                            tmp_field_type = 'time'
                            if by_import_template:
                                tmp_default_note_to_add = tools.ustr(_('Cell must be formatted as hh:mm')) 
                        else:
                            #Khởi gán tên model = tên model của class export
                            tmp_model_name = self.resource
                            #Khởi gán kiểu dữ liệu của column = False
                            tmp_field_type = False
                            #Khởi gán required của field = False
                            tmp_required = False
                            #Khởi gán cần update = True
                            tmp_need_update_required_val = True
                            tmp_is_child_field_of_one2many = False 
                            for child_field_name in tmp_fields_arr:
                                if not tmp_model_name:
                                    break
                                #Tìm field tương ứng
                                tmp_field_obj = field_pool.search([('model_id.model','=',tmp_model_name),
                                                                   ('name','=',child_field_name)],limit=1)
                                #Gán lại model, type, required cho column đó
                                tmp_model_name = tmp_field_obj.relation
                                tmp_field_type = tmp_field_obj.ttype
                                if tmp_need_update_required_val:
                                    tmp_required = tmp_field_obj.required
                                #Nếu kiểu field là many2many/many2one thì không cho update required nữa do required
                                    #tùy vào việc field many2many/many2one có required hay không
                                if tmp_field_type in ('many2many','many2one'):
                                    tmp_need_update_required_val = False
                                #Ngược lại nếu là kiểu one2many
                                elif tmp_field_type == 'one2many':
                                    tmp_is_child_field_of_one2many = True
                                    #Nếu trong trường hợp import mà chưa có cột /id của field one2many đó thì tự động bổ sung
                                    if by_import_template:
                                        tmp_add_field = '%s/id' % (tmp_fields_arr[0])
                                        if tmp_add_field not in field_names:
                                            tmp_add_heading = False
                                            if s_field_heading :
                                                tmp_add_heading = '%s/ID' % (s_field_heading .split('/')[0])
                                            else:
                                                tmp_add_heading = self.env['ir.exports.line'].get_display_full_name_of_field(model_obj=tmp_field_obj.model_id,
                                                                                                field_name=tmp_add_field)['field_heading']
                                            if len(tmp_fields_arr) > 1:
                                                field_names.append(tmp_add_field)
                                                fields_des_dict_lst.append({'name':tmp_add_field, 'heading':tmp_add_heading,
                                                                  'type': 'integer', 'empty_if_false':False,
                                                                  'note':default_id_column_note})
                                            else:
                                                s_field_name = tmp_add_field
                                                s_field_heading = tmp_add_heading
                                                tmp_default_note_to_add = default_id_column_note
                                                tmp_field_type = 'integer'
                            
                            if by_import_template:
                                #Nếu là field bắt buộc nhập dữ liệu
                                if tmp_required:
                                    tmp_required_note = _('Required to enter a value for this column')
                                    #Nếu field đó là kiểu one2many thì cập nhật lại giá trị cho ghi chú 
                                    if len(tmp_fields_arr) > 1 and tmp_is_child_field_of_one2many:
                                        tmp_parent_column = '%s/id' % tmp_fields_arr[0]
                                        #Nếu không có cột tmp_parent_column trong số các cột import
                                        if  tmp_parent_column not in field_names:
                                            tmp_required_note = ''
                                        else:
                                            tmp_required_note = _('If column %s has a value, %s') % (tmp_parent_column,tmp_required_note.lower())
                                            
                                    tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                                            default_note=tools.ustr(tmp_required_note), 
                                                            user_note=False) 
                                #Nếu kiểu field là date
                                if tmp_field_type == 'date':
                                    tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                            default_note=tmp_default_note_to_add, 
                                            user_note=tools.ustr(_('Cell must be formatted as YYYY-MM-DD'))) 
                                #Nếu kiểu field là datetime
                                elif tmp_field_type == 'datetime':
                                    tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                            default_note=tmp_default_note_to_add, 
                                            user_note=tools.ustr(_('Cell must be formatted as YYYY-MM-DD HH:mm:SS. The input value must be converted to time zone UTC 0'))) 
                                #Ngược lại nếu kiểu field là many2many
                                elif tmp_field_type == 'many2many':
                                    tmp_display_mode = self.vks_get_many2many_export_mode(m_model_name=tmp_field_obj.model_id.model,
                                                                            m_field_name=tmp_field_obj.name)
                                    if tmp_display_mode=='one_line':
                                        tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                            default_note=tmp_default_note_to_add, 
                                            user_note=tmp_import_note_for_many2many_field)
                                #Nếu kiểu field là boolean:
                                elif tmp_field_type == 'boolean':
                                    tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                            default_note=tmp_default_note_to_add, 
                                            user_note=tools.ustr(_('If correct, please enter TRUE or 1. Otherwise, please enter FALSE or 0')))
                                elif tmp_field_type == 'binary':
                                    tmp_b_mode = self.vks_get_binary_field_export_param(m_model_name=tmp_field_obj.model_id.model,
                                                                            m_field_name=tmp_field_obj.name)['b_mode']
                                    if tmp_b_mode=='url':
                                        tmp_b_mode = _("""
- If the value is a url, please enter http or https correctly.
- If the value is an local path, the value can be entered in one of the following ways:
+ Way 1: Enter the full path.
+ Way 2: Enter the relative path according to the syntax: module_name%spath_to_file_in_the_module, e.g vks_import_excel%sstatic/src/Test Image OK.jpg
""") % (VKS_STR_SPLIT_MODULE_IN_PATH,VKS_STR_SPLIT_MODULE_IN_PATH)
                                        tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                            default_note=tmp_default_note_to_add, 
                                            user_note=tmp_b_mode)
                                elif tmp_field_type == 'json':
                                    tmp_json_note = _("""
- Enter value according to the following syntax: {'Key 1':Value 1, 'Key 2':Value 2,..., 'Key n':Value n}.
- In the above syntax, key can be id or name e.g. {'3': 20.0, 'Project 2': 80.0}
""")
                                    tmp_default_note_to_add = self.merge_default_note_and_user_note(
                                        default_note=tmp_default_note_to_add, 
                                        user_note=tmp_json_note)
                        
                    except Exception as e:
                        tmp_default_note_to_add = tmp_default_note_to_add 
                
                field_names.append(s_field_name )
                tmp_fields_infors = {'name':s_field_name ,'heading':s_field_heading,
                                     'type':tmp_field_type, 'empty_if_false':child_field.empty_if_false,
                                 }
                if tmp_field_type == 'binary':
                    tmp_fields_infors['ex_width'] = 50
                    
                if by_import_template:
                    tmp_fields_infors['note'] = self.merge_default_note_and_user_note(
                                                    default_note=tmp_default_note_to_add, 
                                                    user_note=child_field.import_note)
                fields_des_dict_lst.append(tmp_fields_infors)
            
            
            export_data = []
            temp_data = False
            
            #Nếu bao gồm việc xuất dữ liệu
            if include_data:
                #Nếu không truyền domain thì lấy domain theo domain đã được thiết lập ở report này
                if special_domain == None:
                    if self.related_filter:
                        if self.related_filter.domain:
                            str_tmp_domain = self.related_filter.domain
                            #Replace các biến đặc biệt khi lập domain để tránh lỗi
                            vks_excel_today = fields.Date.context_today(self.with_context(tz='UTC')) 
                            str_tmp_domain = str_tmp_domain.replace('context_today()','vks_excel_today')
                            str_tmp_domain = str_tmp_domain.replace('.to_utc()','')
                            str_tmp_domain = str_tmp_domain.replace('datetime.datetime.combine','datetime.combine')
                            str_tmp_domain = str_tmp_domain.replace('datetime.time','vks_dt_extend.time')
                            str_tmp_domain = str_tmp_domain.replace('uid',str(self._uid))
                            #Xây dựng domain
                            special_domain = eval(str_tmp_domain)
                        else:
                            special_domain = []
                        
                        #Thêm điều kiện sắp xếp theo bộ lọc nếu có
                        if not str_sort_condition:
                            str_sort_condition = self.related_filter.sort
                            if str_sort_condition and str_sort_condition!='' and str_sort_condition !='[]':
                                str_sort_condition = self.vks_standardized_sort_cond(
                                                        sort_condition=common_method_pool.vks_convert_string_to_list(
                                                                        str_org_list=str_sort_condition),
                                                        src_sort_type='filter')
                            else:
                                str_sort_condition = False
                        
                        #Cập nhật thêm context nếu có
                        str_ctx_extend = self.related_filter.context
                        if str_ctx_extend and str_ctx_extend!='' and str_ctx_extend !='{}':
                            local_context = common_method_pool.vks_merge_two_dict(
                                                org_dict=local_context,
                                                new_dict=common_method_pool.vks_convert_string_to_dict(
                                                        str_org_dict=str_ctx_extend))
                    else:
                        special_domain = []
                
                #Truyền các điều kiện đặc biệt vào context phục vụ tìm kiếm bản ghi hết hiệu lực và đảm bảo giờ xuất ra mặc định là UTC0
                local_context.update({'tz':'UTC'})
                if 'active_test' not in local_context:
                    local_context.update({'active_test':False})
                
                record_ids = self.env[self.resource].with_context(local_context).search(special_domain,order=str_sort_condition)
                if record_ids:
                    export_data = record_ids.export_data(field_names).get('datas', [])
                    #Nếu truyền điều kiện sắp xếp đặc biệt
                    all_sort_conditions = local_context.get('special_sort_excel_condition',False)
                    if all_sort_conditions:
                        for child_sort_condition in  all_sort_conditions:
                            export_data = sorted(export_data, key=itemgetter(child_sort_condition['sort_index']),
                                            reverse=child_sort_condition['sort_reverse'])
                    
            is_hide_technical_row = False
            #Nếu không xuất dữ liệu theo template import
            if not by_import_template:
                is_hide_technical_row = True
            
            export_file_name = False
            #Nếu chỉ cần lấy workbook và các số liệu tham chiếu để phục vụ cho mục đích khác
            if local_context.get('only_need_workbook',False):
                export_file_name = False
            else:
                export_file_name = custom_file_name or self.vks_default_export_excel_name(export_obj=self)
                    
            #Ghi dữ liệu ra excel
            temp_data = self.from_data(fields=field_names,rows=export_data,
                                        fields_des_dict_lst=fields_des_dict_lst,
                                        is_hide_technical_row=is_hide_technical_row,
                                        att_file_name=export_file_name,
                                        res_id=res_id,s_export_obj=self)
            
            #Nếu không cần tạo file đính kèm
            if not export_file_name:
                return temp_data
            
            att_obj = temp_data['att_obj']
            
            #Nếu chỉ định tên file tức là cần trả về id file đính kèm
            if custom_file_name:
                if not local_context.get('vks_need_down_e_direct',False):
                    return att_obj
                
            #Nếu không xuất file theo import template thì mới lưu file
            if not by_import_template:
                self.sudo().write({'message_main_attachment_id':att_obj.id})
            
            return common_method_pool.make_down_load_action_extend(att_obj=att_obj)

    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý khi người dùng muốn export dữ liệu cũ
    def export_old_file(self):
        return self.env['common.method'].make_down_load_action_extend(att_obj=self.message_main_attachment_id)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý khi bấm nút xuất dữ liệu từ giao diện
    def vks_export_to_save(self):
        return {
            'name': _('Export data'),
            'res_model': 'vks.select.export.method.popup',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'context':  self.env['common.method'].standardized_context_for_build_action_view(special_context=self._context)
        }
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý khi bấm nút Xuất dữ liệu và gửi mail
    def vks_export_to_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        if self.message_main_attachment_id :
            try:
                template_id = ir_model_data.get_object_reference('vks_import_excel', 'vks_email_template_export_excel_file')[1]
            except:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except:
                compose_form_id = False
            ctx = dict()
            ctx.update({
                        'default_model': 'ir.exports',
                        'default_attachment_ids': [(6, 0, [self.message_main_attachment_id.id] )],
                        'default_res_ids': self.ids,
                        'default_use_template': bool(template_id),
                        'default_template_id': template_id,
                        'default_composition_mode': 'comment'
                        })

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form' )],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
                }
        else:
            raise UserError(_("""There is no file found for attachment. Please click on "Export Data" button and select the option "Latest and Save"."""))

    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý export ra excel khi gọi từ form export của Odoo 
    @api.model
    def export_to_excel_from_export_base_form(self,export_type_selected,export_id,record_ids_to_export,
                                              sort_condition):
        
        str_sort_condition = self.vks_standardized_sort_cond(sort_condition=sort_condition,src_sort_type='view')
        
        by_import_template=False
        if export_type_selected =='edit':
            by_import_template=True
        export_obj=self.env['ir.exports'].browse(export_id)
        res=export_obj.export_with_domain(by_import_template=by_import_template, include_data=True,
                                        special_domain=[('id','in',record_ids_to_export)],
                                        str_sort_condition=str_sort_condition)
        return res['url']
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    def unlink(self):
        for data in self:
            #Xóa các line trước để đảm bảo các định danh liên quan của các line cũng phải được xóa để tránh lỗi update module
            data.export_fields.unlink()
            #Xóa bản ghi gốc
            super(IrExports,data).unlink()
        return True
    
class IrExportsLine( models.Model):
    _inherit = 'ir.exports.line'
    _order = 'sequence, id asc'

    def get_fields( self ):
        return []
    
    related_field = fields.Many2one('ir.model.fields', string='Field',help='Specify the data field to export')
    heading = fields.Char( string="Label", size=512,help='Specify the column header displayed in the output file',translate=True)
    sequence = fields.Integer( 'Sequence',help="""
- Specify the order of columns displayed in the output file.
- To ensure data export without line errors, it is necessary to set the sequence number for fields requiring data entry to be smaller than the sequence number of fields where data entry is not required.
""")
    name = fields.Char(string='Technical name', help="""
- Specify the exact output data field.
- Use / if you want to export multi-level data, for example: job_id/salary_formula/code
""")
    import_note = fields.Text(string='Import instructions', help="""
Specify instructions for user to enter value to import into the system.
""",translate=True)
    
    empty_if_false = fields.Boolean(string='Empty if false', help="""
If selected, when exporting the file, if this cell data has a false value, it will be converted to an empty string.
""",default = True)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý khi onchange field related_field
    @api.onchange('related_field')
    def onchange_related_object(self):
        if self.related_field:
            self.name =  self.related_field.name
            self.heading = self.env['ir.model.fields'].get_description_of_field_in_lang(
                                                            field_obj=self.related_field, 
                                                            lang=self.env.lang) 
        else:
            self.name =''
            self.heading = ''
        return {}
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    @api.model
    def create(self, vals):
        vals = self.process_before_save(vals=vals,data_obj=False)
        return super(IrExportsLine,self).create(vals)
    
    #Thêm bởi Tuấn - 02/10/2023 - Ghi đè hàm của Odoo
    def write(self, vals):
        for data in self:
            tmp_vals = vals.copy()
            tmp_vals = self.process_before_save(vals=tmp_vals, data_obj=data)
            super(IrExportsLine, data).write(tmp_vals)
        return True
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý dữ liệu trước khi lưu
    @api.model
    def process_before_save(self,vals,data_obj):
        #Gán quyền hạn admin để truy vấn
        self = self.sudo()
        #Nếu thay đổi related_field thì cập nhật lại giá trị cho name (trường hợp người dùng chọn related_field và lưu) 
        if 'related_field' in vals and vals['related_field']:
            vals['name'] = self.env['ir.model.fields'].browse(vals['related_field']).name or ''
        #Ngược lại nếu thay đổi giá trị name (trong trường hợp người lưu danh sách từ chức năng export chuẩn của Odoo) 
        elif 'name' in vals:
            #Chuẩn hóa tên kỹ thuật để phù hợp với việc import và export custom
                #Nếu có hậu tố /display_name thì loại trừ hậu tố này để phù hợp với hướng dẫn import
            st_name = vals['name']
            if st_name:
                st_name = st_name.replace('/display_name','')
                vals['name'] = st_name
            
            export_obj = self.export_id
            if not export_obj:
                export_obj = self.env['ir.exports'].browse(vals['export_id'])
            #Tìm model export
            model_obj = False
            #Nếu đã có sẵn model thì lấy ra model
            if export_obj.related_object:
                model_obj = export_obj.related_object
            #Nếu chưa có thì phải tìm model dựa vào resource của export_obj
            else:
                model_obj = self.env['ir.model'].search([('model','=',export_obj.resource)],limit=1)[0]
            if model_obj:
                tmp_vals = self.get_display_full_name_of_field(model_obj=model_obj, field_name=st_name)
                if tmp_vals['field_obj']:
                    vals['related_field'] = tmp_vals['field_obj'].id
                if (not data_obj) and vals.get('heading',False)==False:
                    vals['heading'] = tmp_vals['field_heading']
        return vals
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy tên hiển thị của 1 field kỹ thuật
    @api.model
    def get_display_full_name_of_field(self,model_obj,field_name):
        res_vals = {'field_obj':False,'field_heading':False}
        if not field_name or not model_obj:
            return res_vals
        tmp_disp_name = ''
        ir_fields_pool = self.env['ir.model.fields'].sudo()
        model_pool = self.env['ir.model'].sudo()
        tmp_arr_field = field_name.split('/')
        tmp_model_obj = False
        tmp_model_obj = model_obj
        tmp_field_obj = False
        for child_val in tmp_arr_field:
            if child_val == '.id':
                child_val = 'id'
            tmp_field_obj = ir_fields_pool.search([('name','=',child_val),('model_id','=',tmp_model_obj.id)],limit=1)[0]
            tmp_disp_name += '%s/' % (ir_fields_pool.get_description_of_field_in_lang(field_obj=tmp_field_obj, lang=self.env.lang))
            if tmp_field_obj.relation:
                tmp_model_obj = model_pool.search([('model','=',tmp_field_obj.relation)],limit=1)[0]
        res_vals['field_heading'] = tmp_disp_name[:-1]
        if len(tmp_arr_field) == 1:
            res_vals['field_obj'] = tmp_field_obj
        return res_vals

class VKSSelectExportMethodPopup(models.TransientModel):
    _name='vks.select.export.method.popup'    
    vks_export_method = fields.Selection([('last_one','Last One'),
                                     ('template_only','Template Only'),
                                     ('template_and_data','Template And Data'),
                                     ('latest_save','Latest and Save')],
        string='How to export data',default='latest_save',required=True)                 
    
    #Thêm bởi Tuấn - 02/10/2023
    def download_file(self):
        vks_context = dict(self._context) or {}
        if vks_context and vks_context.get('active_id',False):
            export_obj=self.env['ir.exports'].browse(vks_context.get('active_id',False))
            selected_export_option = self[0].vks_export_method
            #Nếu kiểu export là tải về dữ liệu của lần xuất dữ liệu gần nhất
            if selected_export_option =='last_one':
                res=export_obj.export_old_file()
            #Nếu chỉ xuất template import (không bao gồm data)
            elif selected_export_option =='template_only':
                res=export_obj.export_with_domain(by_import_template=True,include_data=False)
            #Nếu xuất dữ liệu theo template phục vụ import
            elif selected_export_option =='template_and_data':
                res=export_obj.export_with_domain(by_import_template=True,include_data=True)
            #Nếu xuất dữ liệu và lưu lại     
            else:
                res=export_obj.export_with_domain(include_data=True)
            return res

#-------------------------------------------------------Các prototype về xử lý thread-----------------------------------------------------------------

class VksProcessByThreadBasic(models.Model):
    _name = 'vks.process.by.thread.basic'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Co ban xu ly theo thread'
    _log_access = True
    
    name = fields.Char(string='Name',tracking=True)
    vks_thread_start_time = fields.Datetime('Processing begin on',copy = False,readonly=True,
        help='The time the last thread of this record started processing')
    process_state = fields.Selection(VKS_STATE_THREAD_LIST,string='Processing status',copy = False,readonly=True,default='to_do')
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm gọi khi bấm xử lý dữ liệu trên giao diện
    def process_data_main_method(self):
        self.env['common.method'].calc_data_by_thread_common(ref_objs=self,
                    method_called_name='process_data_special_method',
                    flag_field_name = 'process_state')
        
        return True
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý dữ liệu dưới dạng thread
    def process_data_special_method(self): 
        raise UserError(VKS_STR_METHOD_NOT_DEF_ERROR % ('process_data_special_method'))
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm reset trạng thái xử lý để xử lý lại khi quá trình xử lý bị ngắt ngang
    def action_reset_process_state(self):
        for data in self:
            super(VksProcessByThreadBasic,data).write({'process_state':'to_do'})
        return True
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý khi bấm nút Download file trên form
    def download_file_after_processed(self):
        for data in self:
            return self.env['common.method'].make_down_load_action_extend(att_obj=data.message_main_attachment_id)