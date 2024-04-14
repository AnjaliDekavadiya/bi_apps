
from odoo import fields, http, _
from odoo.http import request

from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError
from odoo.tools import date_utils, groupby as groupbyelem
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import OR

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.mail import _message_post_helper

class FleetPassengersChecklist(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user = request.env.user        

        if 'fleet_attendance_count' in counters:
            fleet_attendance_count = request.env['fleet.attendance'].search_count(self._get_fleet_attendance_domain(user)) \
                if request.env['fleet.attendance'].check_access_rights('read', raise_exception=False) else 0
            
            values['fleet_attendance_count'] = fleet_attendance_count or '0'

        return values
    
    def _get_fleet_attendance_domain(self, user):
        return [
            ('user_id', '=', user.id)
        ]

    @http.route(['/my/fleet_attendances', '/my/fleet_attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_fleet_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        FleetAttendance = request.env['fleet.attendance']

        domain = [('user_id','=',user.id)]
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }

        searchbar_inputs = { 
            'date': {'input': 'create_date', 'label': _('Search in Create Date')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},            
            'completed': {'label': _('Completed'), 'domain': [('state', '=', 'completed')]},            
        }
        # count for pager
        fleet_attendance_count = FleetAttendance.search_count(domain)

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('date', 'all'):                
                search_domain = OR([search_domain, [('create_date', 'ilike', search)]])
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # make pager
        pager = portal_pager(
            url="/my/fleet_attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=fleet_attendance_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        fleet_attendances = FleetAttendance.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_visit_card_history'] = fleet_attendances.ids[:100]
        values.update({
            'date': date_begin,
            'fleet_attendances': fleet_attendances.sudo(),
            'page_name': 'fleet_attendances',
            'pager': pager,
            'filterby': filterby,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,            
            'default_url': '/my/fleet_attendances',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,            
        })
        return request.render("fleet_attendance_checklist.fleet_attendances", values)
    
    @http.route(['/my/fleet_attendance/<int:attendance_id>'], type='http', auth="public", website=True)
    def portal_my_fleet_attendance(self, attendance_id=None, access_token=None, message=False, download=False, **kw):    
        try:
            fleet_attendance_sudo = self._document_check_access('fleet.attendance', attendance_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')                
                
        if fleet_attendance_sudo:
            now = fields.Date.today().isoformat()            
            session_obj_date = request.session.get('view_attendance_%s' % fleet_attendance_sudo.id)          
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_attendance_%s' % fleet_attendance_sudo.id] = now
                body = _('Viewed by customer %s') % fleet_attendance_sudo.partner_id.name
                _message_post_helper(
                    "fleet.attendance",
                    fleet_attendance_sudo.id,
                    body,
                    token=fleet_attendance_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=fleet_attendance_sudo.user_id.sudo().partner_id.ids,
                )

        report_type = kw.get('report_type')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=fleet_attendance_sudo, report_type=report_type, report_ref='fleet_attendance_checklist.action_report_fleet_attendance', download=download)
        
        if fleet_attendance_sudo.state in ('draft', 'confirmed', 'cancel'):
            history = request.session.get('my_visit_card_history', [])
        else:
            history = request.session.get('my_visit_card_history', [])

        values = {
            'fleet_attendance': fleet_attendance_sudo,
            'message': message,
            'token': access_token,            
            'bootstrap_formatting': True,
            'driver_id': fleet_attendance_sudo.driver_id.id,
            'report_type': 'html',
            'action': fleet_attendance_sudo._get_portal_return_action(),
        }
        if fleet_attendance_sudo.company_id:
            values['res_company'] = fleet_attendance_sudo.company_id
        values.update(get_records_pager(history, fleet_attendance_sudo))
        return request.render('fleet_attendance_checklist.fleet_attendance', values)

    @http.route(['/my/fleet_attendance/create_new'], type='http', auth="user", website=True)
    def portal_my_create_new_fleet_attendance(self, access_token=None):
        if not request.session.uid:
            return {'error': 'anonymous_user'}
        
        user = request.env.user
        partner = request.env.user.partner_id 
        vehicle = request.env["fleet.vehicle"].sudo().search([('driver_id', '=', partner.id)], limit=1)
        if not vehicle:
            user = request.env.user.partner_id
            values = {
                'user': user,
                'page_name': 'no_vehiccle_found',
            }
            return request.render("fleet_attendance_checklist.no_vehiccle_fleet_attendance", values)    
        vals = {
            'user_id': user.id,
            'driver_id': partner.id,
            'vehicle_id': vehicle.id,
        }
        attendance = request.env['fleet.attendance'].sudo().create(vals)
        attendance.sudo().load_line_ids()
        return request.redirect('/my/fleet_attendance/%s?token=%s' % (attendance.id, attendance.access_token))

    @http.route(['/my/fleet_attendance/error_message'], type='http', auth="user", website=True)
    def portal_error_fleet_attendance(self, access_token=None):
        if not request.session.uid:
            return {'error': 'anonymous_user'}

        user = request.env.user.partner_id
        values = {
            'user': user,
            'page_name': 'error_fleet_attendance',
        }
        return request.render("fleet_attendance_checklist.error_fleet_attendance", values)

    @http.route(['/my/fleet_attendance/no_vehiccle_found'], type='http', auth="user", website=True)
    def portal_error_no_vehiccle_found(self, access_token=None):
        if not request.session.uid:
            return {'error': 'anonymous_user'}

        user = request.env.user.partner_id
        values = {
            'user': user,
            'page_name': 'no_vehiccle_found',
        }
        return request.render("fleet_attendance_checklist.no_vehiccle_fleet_attendance", values)