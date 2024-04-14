# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import http
from datetime import date, timedelta, datetime
# from odoo.addons.resource.models.resource import float_to_time
from odoo.addons.resource.models.utils import float_to_time
#import time odoo13


class HelpdeskWorkingHours(http.Controller):

    
    @http.route('/helpdesk_support_ticket', type='http', auth="public", website=True)
    def helpdesk_support_ticket(self, **kw):
#        support_team_id = http.request.env['support.team'].search([('custom_is_default', '=', True)],limit=1) odoo13
        support_team_id = http.request.env['support.team'].sudo().search([('custom_is_default', '=', True)],limit=1)
#        resource_calendar_id = support_team_id.custom_support_team_id odoo13
        resource_calendar_id = support_team_id.custom_support_team_id.sudo()
        dict_vals = {'dayofweek':{},'days': {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday'}}
        for ids in resource_calendar_id.attendance_ids:
            # hour_from = '{0:02.0f}:{1:om02.0f}'.format(*divmod(ids.hour_from * 60, 60))
            hour_from = float_to_time(ids.hour_from)
            from_hour = hour_from.strftime("%H:%M")

            # hour_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(ids.hour_to * 60, 60))
            hour_to = float_to_time(ids.hour_to)
            to_hour = hour_to.strftime("%H:%M")
            if int(ids.dayofweek) in dict_vals['dayofweek']:
                dict_vals['dayofweek'][int(ids.dayofweek)].append(str(from_hour) +'   '+ '-'+ '  '+ str(to_hour))
            else:
                dict_vals['dayofweek'][int(ids.dayofweek)] = [str(from_hour)+'   '+ '-'+ '  '+ str(to_hour)]
        list(dict_vals)
        sorted(dict_vals['dayofweek'])
        date_begin = date.today().isoformat() 
        date_end = (date.today()+timedelta(days=10)).isoformat()
        global_leaves_id = support_team_id.custom_support_team_id.global_leave_ids
        start_date = datetime.strptime(date_begin, '%Y-%m-%d')
        end_date = datetime.strptime(date_end, '%Y-%m-%d')
        # final_date_begin = datetime(2018,12,31,11,0,0)
        # final_date_end = datetime(2018,12,23,0,0,0)
        leaves_id = global_leaves_id.filtered(lambda r: r.date_from >= start_date and r.date_from <= end_date)
        sorted_leaves_id = leaves_id.sorted(key=lambda m: (m.date_from))
        return http.request.render("website_helpdesk_support_ticket.website_helpdesk_support_ticket",{'leaves': resource_calendar_id.global_leave_ids,'dict_vals' : dict_vals,'leaves_id' : sorted_leaves_id})


    # @http.route('/show_all_working_hours', type='http', auth="public", website=True)
    # def show_all_working_hours(self, **kw):
    #   custom_all_support_team_id = http.request.env['support.team'].sudo().search([])
    #   # resource_calendar_id = support_team_id.custom_support_team_id
    #   resource_calendar_ids = custom_all_support_team_id.mapped('custom_support_team_id')

    #   dict_vals = {'days': {0:'Monday',1:'Tuesday',2:'Wednesday',3:'Thursday',4:'Friday'}}
    #   for resource_calendar_id in resource_calendar_ids:
    #       for team_id in custom_all_support_team_id:
    #           for ids in resource_calendar_id.attendance_ids:
    #               hour_from = '{0:02.0f}:{1:02.0f}'.format(*divmod(ids.hour_from * 60, 60))
    #               hour_to = '{0:02.0f}:{1:02.0f}'.format(*divmod(ids.hour_to * 60, 60))
    #               if int(ids.dayofweek) in dict_vals:
    #                   dict_vals[team_id.name] = team_id.name
    #                   dict_vals[team_id.name][int(ids.dayofweek)].append(str(hour_from) +'   '+ '-'+ '  '+ str(hour_to))
    #               else:
    #                   dict_vals[team_id.name] = team_id.name
    #                   dict_vals[team_id.name][int(ids.dayofweek)] = [(str(hour_from) +'   '+ '-'+ '  '+ str(hour_to))]
                        
        

    #   list(dict_vals)
    #   sorted(dict_vals['dayofweek'])

    #   return http.request.render("helpdesk_working_hours.working_hours_view",{'all_support_team_id': resource_calendar_ids,'support_team_id':custom_all_support_team_id,'dict_vals' : dict_vals})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
