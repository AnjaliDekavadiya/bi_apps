# -*- coding: utf-8 -*-

from odoo import api, fields, models
from .common_const import *
from odoo.exceptions import UserError, ValidationError

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    #Thêm bởi Tuấn - 06/11/2023 - Ghi đè hàm của Odoo
    @api.model
    def create(self,vals):
        new_obj = super(MailMail,self).create(vals)
        try:
            #Ghi lại nội dung thông điệp do bản gốc của Odoo chỉ có nội dung body_html của mail chứ không có nội dung cho message
            if not new_obj.mail_message_id.body:
                new_obj.mail_message_id.sudo().write({'body':new_obj.body_html})
        except:
            pass
        return new_obj
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    #Thêm bởi Tuấn - 05/10/2023 - Ghi đè hàm của Odoo
    def unlink(self):
        tmp_sp_id = self.env['common.method'].check_record_with_xml_id_exist(module_name='base',record_name='vks_notification_partner',
                                                    only_get_id=True,need_raise_ex=False,include_admin_permission=True)
        for data in self:
            if data.id == tmp_sp_id:
                raise UserError(VKS_STR_INVALID_ACTION_ERROR)
            else:
                super(ResPartner,data).unlink()
            
        return True
    
class ResUsers(models.Model):
    _inherit = 'res.users'
    
    #Thêm bởi Tuấn - 05/10/2023 - Ghi đè hàm của Odoo
    def unlink(self):
        tmp_su_id = self.env['common.method'].check_record_with_xml_id_exist(module_name='base',record_name='vks_notification_user',
                                                    only_get_id=True,need_raise_ex=False,include_admin_permission=True)
        for data in self:
            if data.id == tmp_su_id:
                raise UserError(VKS_STR_INVALID_ACTION_ERROR)
            else:
                super(ResUsers,data).unlink()
            
        return True
    
    #Thêm bởi Tuấn - 05/10/2023 - Ghi đè hàm của Odoo
    def vks_init_system_notify_channel(self):
        channel_pool = self.env['discuss.channel'].sudo()
        vks_notify_partner_id = self.env['ir.model.data']._xmlid_to_res_id('base.vks_notification_partner')
        channel_info = channel_pool.channel_get([vks_notify_partner_id])
        channel = channel_pool.browse(channel_info['id'])
        return channel
    
class MailMessage(models.Model):
    _inherit = 'mail.message'
    
    #Thêm bởi Tuấn - 02/10/2023 - Hàm xử lý notify chat một thông điệp
    @api.model
    def vks_make_messeage_notify_chat(self,partner_need_send_inbox_ids,mail_message_obj,make_none_model):
        if mail_message_obj and partner_need_send_inbox_ids:
            mes_sudo = mail_message_obj.sudo()
            chat_pool = False
            user_pool = self.env['res.users'].sudo()
            tmp_notify_channel_ids = [] 
            tmp_channel_obj = False
            tmp_user_obj = False
            for child_pn_id in partner_need_send_inbox_ids:
                #Tạo kênh chat với user hệ thống nếu là thông báo thông thường để tránh việc tìm nhầm nhóm chat khiến user không nhận được thông báo
                tmp_user_obj = user_pool.search([('partner_id','=',child_pn_id)],limit=1)[0]
                tmp_channel_obj = tmp_user_obj.vks_init_system_notify_channel()
                if tmp_channel_obj:
                    tmp_notify_channel_ids.append(tmp_channel_obj.id)
            
            #Thông báo cho các kênh chat phù hợp
            if tmp_notify_channel_ids:
                su_env = self.env['common.method'].get_var_using_in_thread(get_cursor=False,get_env=True,
                                                    need_admin_per=True,extend_context=None)['new_env']
                chat_pool = su_env['discuss.channel'].sudo()
                vks_notify_partner_id = self.env['ir.model.data']._xmlid_to_res_id('base.vks_notification_partner')
                if len(tmp_notify_channel_ids)==1:
                    child_c_id = tmp_notify_channel_ids[0]
                    make_none_model = False
                    mes_sudo.write({'subtype_id':1,
                                    'message_type':'comment',
                                    'model': chat_pool._name,
                                    'res_id':child_c_id,
                                    'author_id':vks_notify_partner_id
                                    })
                    chat_pool.browse(child_c_id)._notify_thread(message=mes_sudo)
                else:
                    org_mes_obj = su_env['mail.message'].sudo().browse(mes_sudo.id)
                    mes_copy_vals = False
                    c_mess_obj = False
                    for child_c_id in tmp_notify_channel_ids:
                        #Copy message bên trên thành dạng chat
                        mes_copy_vals = {'subject': mes_sudo.subject,
                                    'body':mes_sudo.body,
                                    'subtype_id':1,
                                    'message_type':'comment',
                                    'model': chat_pool._name,
                                    'res_id':child_c_id,
                                    'author_id':vks_notify_partner_id
                                    }
                    
                        c_mess_obj = org_mes_obj.copy(default=mes_copy_vals)
                        
                        #Hiển thị thông báo trên màn hình của các user liên quan (luôn phải dùng sudo nếu không sẽ lỗi ko đọc được thông điệp)
                        chat_pool.browse(child_c_id)._notify_thread(message=c_mess_obj)
            else:
                chat_pool = self.env['discuss.channel'].sudo()
                        
            #Xử lý message gốc (nếu cần)
            if make_none_model:
                mes_sudo.write({'model': chat_pool._name,'res_id':-1,
                                'subtype_id':1, 'message_type':'comment'})
                    
        return True    