# -*- coding: utf8 -*-

import odoo
from odoo import api, fields, models, _
from .common_const import *
from odoo import tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools.safe_eval import safe_eval as eval_extend
from datetime import datetime
import re
import pytz
import time
import base64
from PIL import Image, ImageEnhance
from io import BytesIO
import xlsxwriter
import os
from odoo.http import request
import ast
import json
import requests
from odoo.addons.base_import.models.base_import import DEFAULT_IMAGE_MAXBYTES
from odoo.modules import get_module_resource
        
class CommonMethod(models.AbstractModel):
    _name='common.method'

#--------------------------------------------Các hàm phục vụ cho việc xử lý các phương thức trong model,view-------------------------------------------------------------
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy link user đang dùng để truy cập
    @api.model
    def get_vks_base_url(self,compare_url_val='NONE'):
        tmp_vks_root_url = request.httprequest.url_root
        tmp_error_content = False
        
        #Cờ xác định log lỗi để debug trên ubuntu khi cần
        tmp_need_log_error = tools.config.options.get('vks_log_error',False)
        
        if compare_url_val not in tmp_vks_root_url:
            if tmp_need_log_error:
                tmp_error_content = """
Odoo url root:%s
url_root: %s
url: %s
base_url: %s
full_path: %s
host: %s
host_url: %s
remote_addr: %s
""" % (compare_url_val,tmp_vks_root_url,request.httprequest.url,request.httprequest.base_url,
       request.httprequest.full_path,request.httprequest.host,request.httprequest.host_url,
       request.httprequest.remote_addr)
        
        else:
            tmp_vks_root_url = compare_url_val
            if tmp_need_log_error:
                tmp_error_content = """
compare_url_val: %s
base_url: %s 
remote_addr: %s
""" % (compare_url_val,request.httprequest.base_url,request.httprequest.remote_addr)
        
        if tmp_error_content:
            self.env['common.log.error'].sudo().create({'module_name':'vks_base','class_name':'common.method',
                                                 'function_name':'get_vks_base_url',
                                                 'error_content':tmp_error_content})
        
        #Loại bỏ dấu / cuối cùng (nếu có)
        if tmp_vks_root_url and tmp_vks_root_url.endswith('/'):
            tmp_vks_root_url = tmp_vks_root_url[:-1]
            
        return {'vks_root_url':tmp_vks_root_url,'vks_full_url':request.httprequest.base_url}
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm kiểm tra 1 record xml_id đã có trong hệ thống hay chưa
    @api.model
    def check_record_with_xml_id_exist(self,module_name,record_name,
            only_get_id=True,need_raise_ex=False,include_admin_permission=True):
        #Giải thích ý nghĩa tham số đầu vào:
            #module_name,record_name: dùng để kiểm tra xml id 
            #only_get_id: chỉ cần lấy id bản ghi
            #need_raise_ex: có cần báo lỗi khi không tìm thấy bản ghi đó hay không
            #include_admin_permission: có cần sử dụng quyền admin để tìm kiếm hay không
        
        if include_admin_permission:
            self = self.sudo()
            
        res_val = None
        try:
            res_val = self.env['ir.model.data'].get_object(module_name, record_name)
            if only_get_id:
                res_val = res_val.id
        except:
            if need_raise_ex:
                raise UserError(_('No record found with xml_id is %s.%s') % (module_name,record_name))
            else:
                res_val = None
            
        return res_val
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm phân giải xml_id thành module_name và record_name
    @api.model
    def analytic_xml_id(self,str_xml_id):
        tmp_arr = str_xml_id.split(VKS_SPLIT_XML_ID_CHAR)
        return {'module_name':tmp_arr[0],'record_name':tmp_arr[1]}
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm trả về 1 đối tượng dựa vào xml_id của nó
    @api.model
    def get_special_object_by_xml_id(self,str_xml_id,
            only_get_id=False,need_raise_ex=True,include_admin_permission=True):
        #Ý nghĩa tham số đầu vào: tương tự các hàm analytic_xml_id và check_record_with_xml_id_exist và
        
        tmp_dict = self.analytic_xml_id(str_xml_id=str_xml_id)
        return self.check_record_with_xml_id_exist(module_name=tmp_dict['module_name'],
            record_name=tmp_dict['record_name'],only_get_id=only_get_id,
            need_raise_ex=need_raise_ex,include_admin_permission=include_admin_permission)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy view bởi xml_id
    @api.model
    def get_special_view_by_xml_id(self,str_xml_id,
            only_get_id=True,need_raise_ex=True,include_admin_permission=True):
        #Ý nghĩa tham số đầu vào: tương tự hàm get_special_object_by_xml_id
        
        return self.get_special_object_by_xml_id(str_xml_id=str_xml_id, only_get_id=only_get_id, 
                    need_raise_ex=need_raise_ex, include_admin_permission=include_admin_permission)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy mail template bởi xml_id
    @api.model
    def get_special_mail_template_by_xml_id(self,str_xml_id,
            only_get_id=False,need_raise_ex=True,include_admin_permission=False):
        #Ý nghĩa tham số đầu vào: tương tự hàm get_special_object_by_xml_id
        
        return self.get_special_object_by_xml_id(str_xml_id=str_xml_id, only_get_id=only_get_id, 
                    need_raise_ex=need_raise_ex, include_admin_permission=include_admin_permission)
    
    #Thêm bởi Tuấn - 05/10/2023 - Hàm tạo mới 1 record với kèm xml_id chỉ định
    @api.model
    def create_record_with_xml_id(self,model_name,module_name,record_name,vals):
        #Giải thích ý nghĩa tham số đầu vào:
            #model_name : tên model (ví dụ hr.employee) để biết tạo record cho class nào
            #module_name,record_name: dùng để tạo xml id cho bản ghi được tạo
            #vals: tính chất tương tự hàm create và write của Odoo
            
        #Gán quyền admin 
        su_class = self.sudo()
        #Kiểm tra record xml_id có hay chưa
        des_obj = su_class.check_record_with_xml_id_exist(module_name=module_name,record_name=record_name,only_get_id=False)
        #Nếu chưa có
        if not des_obj:
            #Tạo bản ghi mới
            des_obj = su_class.env[model_name].with_context(mail_create_nosubscribe=True).create(vals)
            #Gán xml_id cho record vừa tạo
            xml_vals = {'module':module_name,'model':model_name,'name':record_name,'res_id':des_obj.id,'noupdate':True}
            su_class.env['ir.model.data'].create(xml_vals)
            
        return des_obj
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm thêm các khung thông điệp không bao gồm phần lên công việc cho formview
    @api.model
    def make_vks_chat_div_for_view(self,str_view_xml_id,org_text,
            tmp_view_obj=False):
        #Ý nghĩa tham số đầu vào: tương tự hàm replace_company_search_cond_for_view
        
        if not tmp_view_obj:
            tmp_view_obj = self.get_special_view_by_xml_id(str_xml_id=str_view_xml_id,only_get_id=False)
            
        str_tmp_view_def = tmp_view_obj.arch
        str_new_text = """
            <div name="vks_chat_div" class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="message_ids"/>
            </div>
"""
        
        str_tmp_view_def = str_tmp_view_def.replace(org_text,str_new_text)
        
        tmp_view_obj.write({'arch':str_tmp_view_def})
        
        return tmp_view_obj
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm thêm các khung thông điệp bao gồm cả phần lên công việc cho formview
    @api.model
    def make_vks_activity_div_for_view(self,str_view_xml_id,org_text,
            tmp_view_obj=False):
        #Ý nghĩa tham số đầu vào: tương tự hàm replace_company_search_cond_for_view
        
        if not tmp_view_obj:
            tmp_view_obj = self.get_special_view_by_xml_id(str_xml_id=str_view_xml_id,only_get_id=False)
            
        str_tmp_view_def = tmp_view_obj.arch
        str_new_text = """
            <div name="vks_chat_div" class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
"""
        
        str_tmp_view_def = str_tmp_view_def.replace(org_text,str_new_text)
        
        tmp_view_obj.write({'arch':str_tmp_view_def})
        
        return tmp_view_obj
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuẩn hóa context để tránh xung đột biến khi tạo action để view đối tượng khác
    @api.model
    def standardized_context_for_build_action_view(self,special_context):
        sta_context = False
        if special_context:
            sta_context = special_context.copy()
            sta_context.pop('group_by',False)
            sta_context.pop('orderedBy',False)
            sta_context.pop('auto_unfold',False)
            sta_context.pop('search_disable_custom_filters',False)
            sta_context.pop('tree_view_ref',False)
            sta_context.pop('form_view_ref',False)
            sta_context.pop('kanban_view_ref',False)
            sta_context.pop('search_view_ref',False)
        else:
            sta_context = {}
            
        return sta_context
    
#--------------------------------------------Các hàm phục vụ cho việc xử lý dữ liệu kiểu dict-------------------------------------------------------------
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuyển string thành dict
    @api.model
    def vks_convert_string_to_dict(self,str_org_dict,is_web_result=False):
        #Ý nghĩa tham số đầu vào:
            #str_org_dict: chuỗi cần chuyển đổi
            #is_web_result: chuỗi đó có phải là kết quả trả về từ web khác hay không (chuỗi này hay có kiểu dict trong dict)
        tmp_f_res = False
        if not str_org_dict:
            return {}
        if is_web_result:
            tmp_f_res = json.loads(str_org_dict)
        else:
            tmp_str_org_dict = str_org_dict.replace("\'", "\"")
            tmp_f_res = ast.literal_eval(tmp_str_org_dict)
        
        return tmp_f_res
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm gộp giá trị của 2 dict
    @api.model
    def vks_merge_two_dict(self,org_dict,new_dict):
        if not org_dict:
            return new_dict
        if not new_dict:
            return org_dict
        
        tmp_merge_dict = org_dict.copy()
        tmp_merge_dict.update(new_dict)
        return tmp_merge_dict

#--------------------------------------------Các hàm phục vụ cho việc xử lý dữ liệu kiểu list-------------------------------------------------------------

    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuyển string thành list
    @api.model
    def vks_convert_string_to_list(self,str_org_list):
        if not str_org_list:
            return []
        tmp_str_org_list = str_org_list.replace("\'", "\"")
        return ast.literal_eval(tmp_str_org_list)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tính tổng một danh sách
    @api.model
    def vks_sum_a_list(self,org_lst):
        #Ý nghĩa tham số đầu vào:
            #org_lst: danh sách cần tính toán
        
        res_val = 0.0
        
        if org_lst:
            res_val = sum(org_lst)
                
        return res_val
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tính giá trị trung bình một danh sách
    @api.model
    def vks_average_a_list(self,org_lst):
        #Ý nghĩa tham số đầu vào:
            #org_lst: danh sách cần tính toán
        
        res_val = 0.0
        
        if org_lst:
            res_val = sum(org_lst)/len(org_lst)
                
        return res_val
    
#--------------------------------------------Các hàm phục vụ cho việc xử lý dữ liệu kiểu datetime-------------------------------------------------------------
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy timezone mặc định
    @api.model
    def get_vks_default_tz(self):
        return 'Asia/Ho_Chi_Minh'
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy timezone của 1 user
    @api.model
    def get_tz_of_user(self, user_id=False,user_obj=False):
        if not user_obj:
            if not user_id:
                user_obj = self.env.user
            else:
                user_obj = self.env['res.users'].browse(user_id)
        partner_obj = user_obj.partner_id
        return self.get_tz_of_partner(partner_obj=partner_obj)
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm lấy timezone của 1 partner
    @api.model
    def get_tz_of_partner(self, partner_id=False,partner_obj=False):
        vks_context = dict(self._context) or {}
        res_tz = vks_context.get('tz', False)
        #Nếu context không quy định timezone
        if not res_tz: 
            if not partner_obj:
                if not partner_id:
                    partner_obj = self.env.user.partner_id
                else:
                    partner_obj = self.env['res.partner'].browse(partner_id)
            res_tz = partner_obj.tz 
            #Nếu user không được thiết lập timezone thì lấy timezone theo server
            if not res_tz:
                res_tz = self.get_vks_default_tz()
        res_tz = tools.ustr(res_tz).encode('utf-8').decode('utf-8')  # make safe for str{p,f}time()
        return res_tz

    #Thêm bởi Tuấn - 02/10/2023 - Hàm Trả về format datetime đã thiết lập của 1 ngôn ngữ
    @api.model
    def get_datetime_format_of_lang(self):
        res_format_date = False
        res_format_time = False
        vks_context = dict(self._context) or {}
        lang = vks_context.get("lang")
        lang_params = {}
        if lang:
            lang_params = self.env['res.lang'].search_read([("code", "=", lang)],["date_format", "time_format"])
        if lang_params:
            res_format_date = lang_params[0].get("date_format", '%B-%d-%Y').encode('utf-8').decode('utf-8')
            res_format_time = lang_params[0].get("time_format", '%I-%M %p').encode('utf-8').decode('utf-8')
        return {'res_format_date':res_format_date,'res_format_time':res_format_time,
                'res_format_date_time': '%s %s' % (str(res_format_date),str(res_format_time))} 
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuyển string sang datetime đã bao gồm múi giờ của người dùng
    @api.model
    def custom_convert_string_to_datetime(self, str_date):
        tmp_value = False
        tmp_value =self.convert_string_to_datetime_without_tz(str_value=str_date)
        tmp_value = fields.Datetime.context_timestamp(self,tmp_value)
        return tmp_value
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuyển string sang datetime không bao gồm múi giờ của người dùng
    @api.model
    def convert_string_to_datetime_without_tz(self, str_value,custom_format=None,only_get_date=False):
        #Giải thích ý nghĩa tham số đầu vào :
            # str_value: chuỗi muốn chuyển thành kiểu datetime
            # only_get_date : nếu True sẽ chỉ lấy giá trị date của kết quả trả về thay vì lấy datetime
            # custom_format : định dạng chuỗi (nếu có ví dụ dd/MM/yyyy)
        
        res_val = False
        if not str_value:
            return res_val
        tmp_str_value = str(str_value)
        if custom_format:
            res_val = datetime.strptime(tmp_str_value, custom_format)
        else:
            try:
                res_val = datetime.strptime(tmp_str_value, DEFAULT_SERVER_DATE_FORMAT)
            except:
                try:
                    res_val = datetime.strptime(tmp_str_value, DEFAULT_SERVER_DATETIME_FORMAT)
                except:
                    try:
                        res_val = datetime.strptime(tmp_str_value, '%Y-%m-%d %H:%M:%S.%f')
                    except:
                        tmp_dt_formats = self.get_datetime_format_of_lang()
                        try:
                            res_val = datetime.strptime(tmp_str_value, tmp_dt_formats['res_format_date_time'])
                        except:
                            res_val = datetime.strptime(tmp_str_value, tmp_dt_formats['res_format_date'])
        if only_get_date:
            res_val = res_val.date()
        return res_val
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm chuyển đổi giá trị chuỗi datetime giữa múi giờ utc và múi giờ của user hiện tại
    @api.model
    def convert_str_datetime_between_utc_and_user_tz(self,str_value,custom_format=None,
                                    convert_type=None,only_get_date=False,remove_tz_infor=True):
        #Giải thích ý nghĩa tham số đầu vào :
            # str_value: chuỗi muốn chuyển thành kiểu datetime
            # only_get_date : nếu True sẽ chỉ lấy giá trị date của kết quả trả về thay vì lấy datetime
            # custom_format : định dạng chuỗi (nếu có ví dụ dd/MM/yyyy)
            # convert_type : kiểu chuyển đổi với quy ước như sau
                #0 : chuyển từ utc sang user_tz
                #1 : chuyển từ user_tz sang utc
                #Khác 2 giá trị trên : bỏ qua tz
            #remove_tz_infor: Có remove tz infor trong giá trị trả về hay không
        
        if not str_value:
            return False
        res_val = False
        #Convert string về dạng  datetime không bao gồm tz
        res_val = self.convert_string_to_datetime_without_tz(str_value=str(str_value), custom_format=custom_format, only_get_date=False)
        
        if convert_type==None:
            convert_type = -1
        #Nếu cần lấy datetime theo múi giờ
        if convert_type in [0,1]:
            #Lấy timezone của người dùng hiện tại
            user_tz_name = self.get_tz_of_user(user_id=self._uid)
            user_tz = pytz.timezone(user_tz_name)
            
            #Nếu chuyển từ utc sang user_tz
            if convert_type ==0:
                res_val = pytz.utc.localize(res_val, is_dst=False)
                res_val = res_val.astimezone(user_tz)
            #Nếu chuyển từ user_tz sang utc
            elif convert_type == 1:
                res_val = user_tz.localize(res_val, is_dst=False)
                res_val = res_val.astimezone(pytz.utc)
        #Nếu chỉ cần lấy date
        if only_get_date:
            res_val = res_val.date()
        elif remove_tz_infor:
            res_val = res_val.replace(tzinfo=None)
        return res_val
    
#--------------------------------Các hàm phục vụ cho việc xử lý dữ liệu truy vấn sql hoặc python code dạng mã lệnh-----------------------------------------

    #Thêm bởi Tuấn - 02/10/2023 - Hàm xây dựng chuỗi cho điều kiện in trong sql từ 1 list - 
        #Ví dụ list là [1,2,3] => Hàm này sẽ trả về (1,2,3)
    @api.model
    def build_in_condition_from_list(self,list_to_convert):
        if not list_to_convert or len(list_to_convert)==0:
            return ''
        str_val = str(tuple(list_to_convert))
        #Nếu list chỉ có 1 phần tử ví dụ [1] thì return dạng (1) thay vì (1,)
        if len(list_to_convert) == 1:
            str_val = str_val[:-2] + ")"
        return str_val
    
#--------------------------------------------Các hàm phục vụ cho việc xử lý dữ liệu để in template, gửi mail----------------------------------------------------
    
    #Thêm bởi Tuấn - 16/10/2023 - Hàm tạo ra base64 string từ 1 đường link
    @api.model
    def make_base64_string_from_url(self,f_url,valid_image_size,include_encode=True):
        tmp_base64_data = False
        #Load from internet
        if f_url.startswith(('http://', 'https://')):
            tmp_base64_data = requests.get(f_url).content
        else:
            #Load from local
            tm_path_arr = f_url.split(VKS_STR_SPLIT_MODULE_IN_PATH)
            if len(tm_path_arr) > 1:
                f_url = get_module_resource(tm_path_arr[0], tm_path_arr[1])
            if (not f_url) or (not os.path.exists(f_url)):
                raise UserError(_('File not found!. Please check path...'))
            else:
                with open(f_url, 'rb') as org_file:
                    tmp_base64_data = org_file.read()
        
        if tmp_base64_data:
            if valid_image_size:
                if len(tmp_base64_data) > DEFAULT_IMAGE_MAXBYTES:
                    raise UserError(_('File size exceeds configured maximum (%s bytes)') % DEFAULT_IMAGE_MAXBYTES)
                else:
                    tmp_v_image = Image.open(BytesIO(tmp_base64_data))
                    w, h = tmp_v_image.size
                    if w * h > 42e6:  # Nokia Lumia 1020 photo resolution
                        raise UserError(_('Image size excessive, imported images must be smaller than 42 million pixel'))
                    
        if include_encode:
            tmp_base64_data = base64.b64encode(tmp_base64_data)
            
        return tmp_base64_data
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo wookbook mới để ghi dữ liệu
    @api.model
    def make_new_wookbook_common(self):
        fp = BytesIO()
        #workbook_obj = xlsxwriter.Workbook(fp)
        workbook_obj = xlsxwriter.Workbook(fp, {'in_memory': True})
        return {'workbook_obj':workbook_obj,'io_stream':fp}
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo tên file phù hợp để lưu
    @api.model
    def make_valid_file_name_for_save(self,file_name,custom_replace_char='_',str_max_length=False):
        #Thay thế các ký tự mà file name của windows không cho phép bằng ký tự custom_replace_char
        lst_invalid_char = ['\\','/',':','*','?','"','<','>','|']
        for child_char in lst_invalid_char:
            file_name = file_name.replace(child_char,custom_replace_char)
        if str_max_length:
            file_name = file_name[0:str_max_length]
        return file_name
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo tên export chuẩn
    @api.model
    def make_export_name_default(self,file_name,file_extension='xlsx',include_datetime=True):
        #Ý nghĩa tham số đầu vào
            #file_name : chuỗi định dùng làm tên file
            #file_extension : kiểu file ví dụ 'xls'
            #include_datetime : có cho thêm ngày tháng hiện tại vào tên file xuất ra hay không
        
        #Thêm ngày tháng vào tên report nhằm tránh việc idm chờ download
        if include_datetime:
            file_name = ("%s_%s") % (file_name,str(datetime.now()))
        #Chắc chắn rằng tên file hợp lệ
        file_name = self.make_valid_file_name_for_save(file_name=file_name)
        #Thêm đuôi mở rộng nếu chưa có
        tmp_str_extension = '.%s' % (file_extension) 
        if tmp_str_extension not in file_name:
            file_name = ("%s%s") % (file_name,tmp_str_extension)
            
        return file_name
    
    #Thêm bởi Tuấn - 06/11/2023 - Hàm tạo đính kèm từ dữ liệu binary
    @api.model
    def make_att_from_binary(self,real_data,download_file_name,file_extension='xlsx',
            include_datetime=False,res_id=-1):
        #Ý nghĩa tham số đầu vào:
            #real_data:dữ liệu để mã hóa
            #download_file_name: tên file download
            #res_id:Id bản ghi tham chiếu để phục vụ cho việc xác định là file đính kèm tạm thời hay không
            #Các tham số khác : tương tự hàm make_export_name_default
            
        export_file_name = self.make_export_name_default(file_name=download_file_name,
                                                file_extension=file_extension,include_datetime=include_datetime)
        
        #b64_tmp_data = base64.encodestring(real_data)
        b64_tmp_data = base64.b64encode(real_data)
        if res_id==-1:
            res_id = 0
        att_obj = self.env['ir.attachment'].create({
                 'name':export_file_name,
                 'datas':b64_tmp_data,
                 'res_id':res_id,
                 'type':'binary'
                 })
        
        return att_obj
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo dữ liệu binary từ wookbook
    @api.model
    def make_binary_data_from_wookbook(self,workbook_obj,io_stream, need_make_att,
            download_file_name,file_extension='xlsx',include_datetime=False,res_id=-1):
        #Ý nghĩa tham số đầu vào:
            #workbook_obj:wookbook 
            #need_make_att: có cần tạo file đính kèm hay ko
            #io_stream: stream dùng để ghi wookbook
            #Các tham số khác: tương tự hàm make_att_from_binary
        
        res_val = False
        workbook_obj.close()
        #io_stream.seek(0)
        #temp_data = io_stream.read()
        temp_data = io_stream.getvalue()
        io_stream.close()
        #Nếu không cần tạo file đính kèm
        if not need_make_att:
            res_val = temp_data
        else:
            #Ngược lại return file đính kèm
            res_val = self.make_att_from_binary(real_data=temp_data, 
                            download_file_name=download_file_name, file_extension=file_extension, 
                            include_datetime=include_datetime,res_id=res_id)   
                
        return res_val
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo link download 1 file
    @api.model
    def make_down_load_link_extend(self,att_obj,custom_download_name=False):
        if not att_obj:
            raise UserError(VKS_STR_ATT_NOT_FOUND)
        if not custom_download_name:
            custom_download_name = att_obj.name
        #tmp_url =   """web/content/?model=ir.attachment&id=%s&filename_field=name&field=datas&download=true&filename=%s""" % (att_obj.id,custom_download_name)
        tmp_url =   """web/content/%s/?filename=%s&download=true""" % (att_obj.id,custom_download_name)
        return tmp_url
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm tạo action down load 1 file
    @api.model
    def make_down_load_action_extend(self,att_obj,custom_download_name=False):
        tmp_url = self.make_down_load_link_extend(att_obj=att_obj)  
        return {'type' : 'ir.actions.act_url',
                'url':   tmp_url,
                #'target': 'self'
                'target': 'download'
    }
        
#----------------------------------------Các hàm xử lý dữ liệu bằng thread--------------------------------------------------------------
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm trả về 1 số biến dùng cho thread
    @api.model
    def get_var_using_in_thread(self,custom_uid=False,get_cursor=True,get_env=True,
                                need_admin_per=False,extend_context=None):
        #Ý nghĩa tham số đầu vào:
            #custom_uid: user cần gán quyền hạn
            #get_cursor:khởi tạo con trỏ database hay không
            #get_env: khởi tạo môi trường mới hay không
            #extend_context: dict context mở rộng nếu có
        vks_context = extend_context or dict(self._context) or {}
        res_vals = {}
        if not custom_uid:
            if need_admin_per:
                custom_uid = SUPERUSER_ID
            else:
                custom_uid = self._uid
        if get_cursor:
            res_vals.update({'new_cr':odoo.sql_db.db_connect(self._cr.dbname).cursor()})
        else:
            res_vals.update({'new_cr':self._cr})
        if get_env:
            res_vals.update({'new_env':api.Environment(res_vals['new_cr'], custom_uid, vks_context)})
        else:
            res_vals.update({'new_env':self.env})
        return res_vals
        
#----------------------------------------Các hàm xử lý dữ liệu liên kết ngoài--------------------------------------------------------------
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm kiểm tra hệ điều hành có phải windows hay không
    @api.model
    def check_os_is_windows(self):
        if os.name=='nt':
            return True
        return False
    
    #Thêm bởi Tuấn - 06/11/2023 - Hàm ghi thông tin binary data ra file tạm để xử lý
    @api.model 
    def save_file(self, name, value):
        type_path = False
        #Check if is window, get template folder
        if self.check_os_is_windows():
            type_path = os.environ['TMP']
        else:
            type_path = '/tmp/file_ttp'
        if not os.path.exists(type_path):
            os.mkdir(type_path)
        path = '%s/%s' % (type_path,name)       
        f = open( path, 'wb+' )
        try:
            f.write(base64.decodebytes(value))
        finally:
            f.close()
        return path