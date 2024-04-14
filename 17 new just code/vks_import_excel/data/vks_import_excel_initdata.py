# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from ..models.common_const import *

class VksImportExcelInitdata(models.AbstractModel):
    _name='vks.import.excel.initdata'
    
    #Thêm bởi Tuấn - 02/10/2023 - Tạo 1 số dữ liệu mặc định khi cài module này
    @api.model
    def vks_import_excel_initdata_method(self):
        tmp_final_res_val = True
        ir_model_pool = self.env['ir.model'].sudo()
        common_method_pool = self.env['common.method'].sudo()
        
        #Thêm khóa để ngăn Odoo thay đổi web.base.url theo người đăng nhập (cực kỳ quan trọng)
        
        tmp_icp_pool = self.env['ir.config_parameter'].sudo()
        
        try:
            tmp_base_url_obj = False
            tmp_base_url_objs = tmp_icp_pool.search([('key','=','web.base.url.freeze')],limit=1)
            if not tmp_base_url_objs:
                tmp_base_url_obj = tmp_icp_pool.create({'key':'web.base.url.freeze','value':'True'})
            else:
                tmp_base_url_obj = tmp_base_url_objs[0]
            tmp_base_url_obj.write({'value':'True'})
                
        except:
            pass
        
        try:
            tmp_obj = common_method_pool.create_record_with_xml_id(model_name='res.partner',module_name='base',
                                record_name='vks_notification_partner',vals={'name':'#System Notification','email':'vkssystem@example.com',
                                                                          'active':False})
            
            common_method_pool.with_context(install_mode=True).create_record_with_xml_id(model_name='res.users',module_name='base',
                                record_name='vks_notification_user',vals={'name':'#System Notification','login':'vkssystem@example.com',
                                                                          'partner_id':tmp_obj.id,'active':False})
        except Exception as e:
            pass
        
        #-------------------------------------Điều chỉnh giao diện 1 số view-----------------------------------------------------
        try:
            common_method_pool.make_vks_chat_div_for_view(str_view_xml_id='vks_import_excel.view_responsibility_of_user_form',
                                org_text='<div name="vks_chat_div"/>',
                                tmp_view_obj=False)
        except:
            pass
        
        try:
            common_method_pool.make_vks_activity_div_for_view(str_view_xml_id='vks_import_excel.view_responsibility_of_user_activity_form',
                                org_text='<div name="vks_chat_div"/>',
                                tmp_view_obj=False)
        except:
            pass
        
        return tmp_final_res_val