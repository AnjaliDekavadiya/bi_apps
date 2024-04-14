# -*- coding: utf-8 -*-

import pytz
from pytz import timezone
from datetime import datetime
import time
import base64

from odoo import http, _
from odoo.http import request
#from odoo import http, modules, tools odoo13
from odoo import tools
#from odoo import models, fields, registry, SUPERUSER_ID odoo13
from odoo import fields, registry, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal

class FleetRequest(http.Controller):
    
    def _convert_to_utc(self, localdatetime, emp):
        check_in_date = datetime.strptime(localdatetime, "%Y-%m-%d  %H:%M:%S")
        timezone_tz = 'utc'
        user_id = request.env['res.users'].sudo().search([('partner_id', '=', int(emp))])
        super_user = request.env['res.users'].sudo().browse(SUPERUSER_ID)
        if user_id.tz:
            timezone_tz = user_id.tz
        elif super_user.tz:
            timezone_tz = super_user.tz
        local = pytz.timezone(timezone_tz)
        local_dt = local.localize(check_in_date, is_dst=None)
        utc_datetime = local_dt.astimezone(pytz.utc)
        return utc_datetime
    
    def update_appointment_get_values(self, post, services, model, make_brands, make_id, model_id, day_match, dict_my, appointees, appointee_id, yearl,sorted_dict_my={}):
        values = {
                'name' : post['customer_id'],
                'email' : post['email'],
                'phone' : post['phone'],
                'date' : post['start_date'],
                'subject' : post['subject'],
                'description' : post['description'],
                'subject' : post['subject'],
                'license_plate': post['license_plate'],
                'type_ids': services,
#                 'service_type': int(service_id),
                'year': post['year'],
                'make_ids': model,
                'brand_ids': make_brands,
                'make': make_id,
                'model': model_id,
                'mileage': post['mileage'],
                'day':day_match,
                'dict_my':dict_my,
                'appointee_ids' : appointees,
                'appointee_id': int(appointee_id),
                'yearl': yearl,
                'sorted_dict_my':sorted_dict_my,
        }
        return values
    
    @http.route(['/fleet_repair_request_management/appointment_get'], type='http', auth="public", methods=['POST'], website=True)
    def appointment_get(self, **post):
        datetime_object = datetime.strptime(post['start_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
        day = fields.Date.from_string(datetime_object).strftime('%A')
        slot_obj = http.request.env['appointment.slot']
        day_match = slot_obj.sudo().search([('day','=', day)])
        event_obj = request.env['calendar.event']
        partner_obj = http.request.env['res.partner']
        appointees = partner_obj.sudo().search([('is_available_for_apointment','=',True)])
        appointee_id = post.get('appointee_id', False)
        if not appointee_id:
            return request.render("fleet_repair_request_management.appointee_msg")
        
        service_obj = http.request.env['fleet.service.type']
        services = service_obj.sudo().search([])
        service_id = post.get('service_type', False)
        
        brand_obj = request.env['fleet.vehicle.model.brand'].sudo().search([])
        make_brands = brand_obj.sudo().search([])
        make_id = post.get('make', False)
        
        model_obj = request.env['fleet.vehicle.model'].sudo().search([])
        model = model_obj.sudo().search([])
        model_id = post.get('model', False)
        
        date_start = datetime.strptime(post['start_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
        dict_my = {}
        for day_m in day_match.slot_line_ids:
            day_slot = date_start +' '+day_m.time+':00'
            start_datetime = self._convert_to_utc(day_slot, appointee_id).strftime("%Y-%m-%d %H:%M:%S")
            book_slots = event_obj.sudo().search([('partner_ids', 'in', [appointee_id]),
                                                  ('custom_slot','=', tools.ustr(day_m.time)),
                                                  ('start_datetime', '=', start_datetime)])
            if book_slots:
                dict_my[day_m.time] = True
            else:
                dict_my[day_m.time] = False
        sorted_dict_my = sorted(dict_my)
        yearl = []
        for i in range(1950, 2025):
            yearl.append((i))
        slot_values = self.update_appointment_get_values(post, services, model, make_brands, make_id, model_id, day_match, dict_my, appointees, appointee_id, yearl,sorted_dict_my)
        return http.request.render('fleet_repair_request_management.fleet_repair_request',slot_values)

    def _get_fleet_request_vals(self, post, team_match, service_type_list_id, Partner, vehicle, appointment):
        vals = {
                    'subject': post['subject'],
                    'team_id' :team_match.id,
                    # 'partner_id' :team_match.leader_id.id,
                    'user_id' :team_match.leader_id.id,
                    'email': post['email'],
                    'phone': post['phone'],
                    'service_type_ids': [(6, 0, service_type_list_id)],
                    'description': post['description'],
                    'partner_id': Partner.id,
                    'license_plate': post['license_plate'],
                    'vehicle_id': vehicle.id or False,
#                    'year': int(post['year']), odoo13
                    'year': str(post['year']),
                    'make_id': post['make'],
                    'model': post['model'],
                    'mileage': post['mileage'],
                    'event_id':appointment.id,
                    'custome_client_user_id': request.env.user.id,
            }
        return vals

    @http.route(['/fleet_repair_request_management/fleet_repair_submitted'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def fleet_repair_submitted(self, **post):
        if not post.get('appointee_id', False):
            return request.render("fleet_repair_request_management.appointee_msg")
        if not post['slot']:
            return request.render("fleet_repair_request_management.time_slot_msg")
        if post['year'] == 'Select Vehicle Year':
                return request.render("fleet_repair_request_management.vehicle_year_msg")
        vales_list = post.keys()
        res = [k for k in vales_list if 'service_type' in k]
        service_type_list_id = []
        for r in res:
            service_type_list_id.append(int(post.get(r)))
        time = post['slot']
        appointee_id = post.get('appointee_id', False)
        date_start = datetime.strptime(post['start_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
        day_slot = date_start +' '+time+':00'
        event_obj = request.env['calendar.event']
        partner_obj = http.request.env['res.partner']

        start_datetime = self._convert_to_utc(day_slot, appointee_id)
        start_datetime_strf = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        book_slots = event_obj.sudo().search([('partner_ids', 'in', [appointee_id]),
                                              ('custom_slot','=', tools.ustr(time)),
                                              ('start_datetime', '=', start_datetime_strf)])
        if appointee_id:
            for book_slot in book_slots:
                partner_match = partner_obj.sudo().search([('is_available_for_apointment','=',True)])
                for person in book_slot.partner_ids:
                    for p in partner_match:
                        if person == p:
                            return http.request.render('fleet_repair_request_management.book_slot')

        appointment = http.request.env['calendar.event'].sudo().create({
                                                    'name': post['subject'],
                                                    'custom_customer_name': request.env.user.partner_id.id,
                                                    'custom_email': post['email'],
                                                    'custom_phone': post['phone'],
                                                    'description': post['description'],
                                                    'partner_ids' : [(6, 0, [int(appointee_id),request.env.user.partner_id.id])],
                                                    'start_datetime' : start_datetime_strf,
                                                    'stop_datetime' : start_datetime_strf,
                                                    'start': start_datetime_strf,
                                                    'stop': start_datetime_strf,
                                                    'custom_slot': tools.ustr(time),
                                                    'duration':0.0,
#                                                     'company_name':request.env.user.company_id.name
                                                     })
        

        service_type_list = request.httprequest.form.getlist('service_type')
        services = []
        for service in service_type_list:
            service_types = [int(service)]
            services.append(service_types)
        vehicle = request.env['fleet.vehicle'].sudo().search([('license_plate','=',post['license_plate'])], limit=1)
        
        cr, uid, context, pool = http.request.cr, http.request.uid, http.request.context, request.env
        if request.env.user.has_group('base.group_public'):
            Partner = request.env['res.partner'].sudo().search([('email', '=', post['email'])], limit=1)
        else:
            Partner = request.env.user.partner_id
        
        if Partner:
            team_obj = http.request.env['fleet.team']
            team_match = team_obj.sudo().search([('is_team','=', True)], limit=1)
            vale = self._get_fleet_request_vals(post, team_match, service_type_list_id, Partner, vehicle, appointment)
            repair = pool['fleet.request'].sudo().create(vale)
            values = {
                'repair':repair
            }
            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if post.get('attachment'):
                    attachments = {
                               'res_name': image.filename,
                               'res_model': 'fleet.request',
                               'res_id': repair,
                               'datas': base64.encodebytes(image.read()),
                               'type': 'binary',
                               #'datas_fname': image.filename,
                               'name': image.filename,
                           }
                    attachment_obj = http.request.env['ir.attachment']
                    attach = attachment_obj.sudo().create(attachments)
            if len(attachment_list) > 0:
                group_msg = _('Customer has sent %s attachments to this Repair Request. Name of attachments are: ') % (len(attachment_list))
                for attach in attachment_list:
                    group_msg = group_msg + '\n' + attach.filename
                group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
                repair.sudo().message_post(body=group_msg,message_type='comment')
            return request.render('fleet_repair_request_management.fleet_thanks_mail_send', values)
        else:
            return request.render('fleet_repair_request_management.fleet_repair_invalid',{})

    def update_service_type_values(self, kw, model, brand, services, appointees, yearl):
        values = {
            'make_ids': model,
            'brand_ids': brand,
            'type_ids': services,
            'appointee_ids' : appointees,
            'yearl':yearl,
        }
        return values

    @http.route(['/page/fleet_repair_request'], type='http', auth="user",website=True)
    def service_type(self, **kw):
        partner_obj = http.request.env['res.partner']
        appointees = partner_obj.sudo().search([('is_available_for_apointment','=',True)])
        services = request.env['fleet.service.type'].sudo().search([])
        brand = request.env['fleet.vehicle.model.brand'].sudo().search([])
        model = request.env['fleet.vehicle.model'].sudo().search([])
        
        yearl = []
        for i in range(1950, 2025):
            yearl.append((i))
        values = self.update_service_type_values(kw, model, brand, services, appointees, yearl)
        return http.request.render('fleet_repair_request_management.fleet_repair_request',values)
       
    # not used odoo13
    # @http.route(['/fleet_repair_request_management/invite'], auth='public', website=True, methods=['POST'])
    # def index_user_invite(self, **kw):
    #     email = kw.get('email')
    #     name = kw.get('name')
    #     cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
    #     user = request.env['res.users'].browse(request.uid)
    #     user_exist = request.env['res.users'].sudo().search([('login','=',str(email))])
    #     vals = {
    #               'user_id':user_exist,
    #             }
    #     if user_exist:
    #         return http.request.render('fleet_repair_request_management.user_alredy_exist', vals)
    #     value={
    #           'name': name,
    #           'email': email,
    #           'invitation_date':datetime.today(),
    #           'referrer_user_id':user.id,
    #           }
    #     user_info_id = self.create_history(value)
    #     base_url = http.request.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069') + '/page/fleet_repair_request_management.user_thanks'
    #     url = "%s?user_info=%s" %(base_url, user_info_id.id)
    #     reject_url = http.request.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069') + '/page/fleet_repair_request_management.user_thanks_reject'
    #     rejected_url = "%s?user_info=%s" %(reject_url, user_info_id.id)
    #     local_context = http.request.env.context.copy()
    #     issue_template = http.request.env.ref('fleet_repair_request_management.email_template_fleet_repair_requested')
    #     local_context.update({'user_email': email, 'url': url, 'name':name,'rejected_url':rejected_url})
    #     issue_template.sudo().with_context(local_context).send_mail(request.uid, force_send=True)
       
    @http.route(['/repair_email/feedback/<int:order_id>'], type='http', auth='public', website=True)
    def feedback_email(self, order_id, **kw):
        values = {}
        values.update({'repair_id': order_id})
        return request.render("fleet_repair_request_management.website_fleet_repair_feedback", values) 
       
    @http.route(['/repair/feedback/'],
                type='http', auth='user', website=True)
    def start_rating(self, **kw):
        partner_id = kw['partner_id']
        user_id = kw['repair_id']
        repair_obj = request.env['fleet.request'].sudo().browse(int(user_id))
        #if partner_id == UserInput.partner_id.id:
        vals = {
              'rating':kw['star'],
              'comment':kw['comment'],
            }
        repair_obj.sudo().write(vals)
        customer_msg = _(repair_obj.partner_id.name + 'has send this feedback rating is %s and comment is %s') % (kw['star'],kw['comment'],)
        repair_obj.sudo().message_post(body=customer_msg)
        return http.request.render("fleet_repair_request_management.successful_feedback")
            
class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self): # odoo11
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        repair = request.env['fleet.request']
        repair_count = repair.sudo().search_count([
        ('partner_id', 'child_of', [partner.commercial_partner_id.id])
          ])
        values.update({
            'repair_count': repair_count,
        })
        return values

#     @http.route()
#     def account(self, **kw):
#         """ Add fleet repair documents to main account page """
#         response = super(website_account, self).account(**kw)
#         partner = request.env.user.partner_id
#         repair = request.env['fleet.request']
#         repair_count = repair.sudo().search_count([
#         ('partner_id', 'child_of', [partner.commercial_partner_id.id])
#           ])
#         response.qcontext.update({
#         'repair_count': repair_count,
#         })
#         return response
#         
    @http.route(['/my/fleet_repairs', '/my/fleet_repairs/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_fleet_repairs(self, page=1, **kw):
        response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        repair_obj = http.request.env['fleet.request']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # count for pager
        repair_count = repair_obj.sudo().search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/fleet_repairs",
            total=repair_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        repairs = repair_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'repairs': repairs,
            'page_name': 'repair',
            'pager': pager,
            'default_url': '/my/fleet_repairs',
        })
        return request.render("fleet_repair_request_management.display_repair_request", values)
       
    @http.route(['/my/repair/<model("fleet.request"):repair>'], type='http', auth="user", website=True)
    def my_repiar(self, repair=None, **kw):
        attachment_list = request.httprequest.files.getlist('attachment')
        repair_obj = http.request.env['fleet.request'].sudo().browse(repair.id)
        for image in attachment_list:
            if kw.get('attachment'):
                attachments = {
                           'res_name': image.filename,
                           'res_model': 'fleet.request',
                           'res_id': repair.id,
                           'datas': base64.encodebytes(image.read()),
                           'type': 'binary',
                           #'datas_fname': image.filename,
                           'name': image.filename,
                       }
                attachment_obj = http.request.env['ir.attachment']
                attachment_obj.sudo().create(attachments)
        if len(attachment_list) > 0:
            group_msg = _('Customer has sent %s attachments to this repair. Name of attachments are: ') % (len(attachment_list))
            for attach in attachment_list:
                group_msg = group_msg + '\n' + attach.filename
            group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
            repair_obj.sudo().message_post(body=group_msg,message_type='comment')
            customer_msg = _('%s') % (kw.get('repair_comment'))
            repair_obj.sudo().message_post(body=customer_msg,message_type='comment')
            return http.request.render('fleet_repair_request_management.fleet_repair_request_successful_send',{
            })
        if kw.get('repair_comment'):
            customer_msg = _('%s') % (kw.get('repair_comment'))
            repair_obj.sudo().message_post(body=customer_msg,message_type='comment')
            return http.request.render('fleet_repair_request_management.fleet_repair_request_successful_send',{
            })
        return request.render("fleet_repair_request_management.display_fleet_repairs", {'repair': repair, 'user': request.env.user,'page_name': 'repair',})

    @http.route(['/get_car_washing_data'], type='json', auth="public", website=True)
    def GetCarWashingData(self, type_id, **post):
        service_type_obj = request.env['fleet.service.type']
        currency_id = request.env.user.company_id.currency_id
        symbol = currency_id.symbol if currency_id else ''
        vals = []

        if type_id:
            service_type_id = service_type_obj.sudo().browse(int(type_id))
            vals.append(service_type_id.name)
            vals.append(service_type_id.service_charges)
            service_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(service_type_id.service_time * 60, 60))
            vals.append(service_time)
            vals.append(service_type_id.service_time)
            vals.append(symbol)

        return vals
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
