import uuid
from odoo import models, fields, api, exceptions, _

class FleetAttendance(models.Model):
    _name = "fleet.attendance"
    _description = "Fleet Attendance"
    _order = "id desc"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    def _default_attendance_name(self):
        return self.env['ir.sequence'].next_by_code('fleet.attendance')

    name = fields.Char(string='Name', default=lambda self: self._default_attendance_name(), help="Sequence of Event")
    user_id = fields.Many2one('res.users', string='Responsible', index=True, tracking=2, default=lambda self: self.env.user)
    driver_id = fields.Many2one("res.partner", string="Driver", tracking=True)
    # states={'draft': [('readonly', False)], 'completed': [('readonly', True)]}
    vehicle_id = fields.Many2one("fleet.vehicle", string='Vehicle', tracking=True)
    # states={'draft': [('readonly', False)], 'completed': [('readonly', True)]}    
    access_token = fields.Char(string='Access Token', default=lambda self: self._get_default_access_token(), copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    trip_state = fields.Selection([
        ('onward_trip', 'Onward Trip'),
        ('return_trip', 'Return Trip'),
        ], string='Direction', readonly=False, copy=False, index=True, tracking=3, default='onward_trip')
    # states={'draft': [('readonly', False)], 'completed': [('readonly', True)]}
    line_ids = fields.One2many('fleet.attendance.line', 'fleet_attendance_id', string='Passengers')
    # states={'draft': [('readonly', False)], 'completed': [('readonly', True)]}
    company_id = fields.Many2one(
        'res.company', 'Company', 
        required=True, index=True, 
        default=lambda self: self.env.company)
    access_url = fields.Char(
        string='Portal Access URL', 
        compute='_compute_access_url',
        help='Portal URL')
    
    def _compute_access_url(self):
        for rec in self:
            rec.access_url = '/my/fleet_attendance/%s' % rec.id

    @api.onchange('driver_id')
    def _onchange_driver(self):        
        for rec in self:
            if rec.driver_id:
                rec.update({'line_ids': [(5, 0, 0)] })
                vehicle = self.env["fleet.vehicle"].sudo().search([('driver_id', '=', rec.driver_id.id)], limit=1)
                passengers = []                
                for passenger in vehicle.passengers_ids:
                    vals = (0, 0,{
                        'partner_id': passenger.partner_id.id,
                        'fleet_attendance_id': rec.id,
                    })
                    passengers.append(vals)
                rec.update({
                    'line_ids' : passengers,
                    'driver_id': rec.driver_id.id,
                    'vehicle_id': vehicle.id if vehicle.id else False,
                })
            else:                
                rec.update({
                    'line_ids': [(5, 0, 0)],
                    'vehicle_id': False,
                    'driver_id': False,
                })

    def load_line_ids(self):
        for rec in self:
            if rec.driver_id:
                rec.update({'line_ids': [(5, 0, 0)] })
                vehicle = self.env["fleet.vehicle"].sudo().search([('driver_id', '=', rec.driver_id.id)], limit=1)
                passengers = []                
                for passenger in vehicle.passengers_ids:
                    vals = (0, 0,{
                        'partner_id': passenger.partner_id.id,
                        'fleet_attendance_id': rec.id,
                    })
                    passengers.append(vals)
                rec.update({
                    'line_ids' : passengers,
                    'driver_id': rec.driver_id.id,
                    'vehicle_id': vehicle.id if vehicle.id else False,
                })
            else:                
                rec.update({
                    'line_ids': [(5, 0, 0)],
                    'vehicle_id': False,
                    'driver_id': False,
                })

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.attendance')
        return super().create(vals)
    
    def _portal_ensure_token(self):
        """ Get the current record access token """
        if not self.access_token:
            self.sudo().write({'access_token': str(uuid.uuid4())})
        return self.access_token

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        url = self.access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url
    
    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from portal. """
        self.ensure_one()
        return self.env.ref('fleet_attendance_checklist.fleet_attendances_action')

    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)


class FleetAttendanceLine(models.Model):
    _name = "fleet.attendance.line"

    fleet_attendance_id = fields.Many2one('fleet.attendance', string='Fleet Attendance Reference', required=True, ondelete='cascade', index=True, copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner")
    checked_in = fields.Boolean('Checked In', default=False)
    checked_out = fields.Boolean('Checked Out', default=False)
    checked_in_time = fields.Datetime('Checked In Time')
    checked_out_time = fields.Datetime('Checked Out Time')
    checked_in_alarm = fields.Boolean('Checked In Alarm', default=False)
    checked_out_alarm = fields.Boolean('Checked Out Alarm', default=False)

    def send_sms(self, type):
        line = self.env['fleet.attendance.line'].sudo().search([('id', '=', int(self.id))])
        if type == 'check_in':
            if line.checked_in and line.checked_in_time and line.partner_id.fleet_alert_phone:
                body = line.partner_id.name + " checked in at "+ str(line.checked_in_time)
                vals = {
                    'partner_id': line.partner_id.id,
                    'number': line.partner_id.fleet_alert_phone,
                    'body': body,
                }            
                sms = self.env['sms.sms'].sudo().create(vals)
                return {
                    'message' : 'success'
                }
            else:
                return {
                    'message' : 'failed'
                }
        if type == 'check_out':
            if line.checked_out and line.checked_out_time and line.partner_id.fleet_alert_phone:
                body = line.partner_id.name + " checked out at "+ str(line.checked_out_time)
                vals = {
                    'partner_id': line.partner_id.id,
                    'number': line.partner_id.fleet_alert_phone,
                    'body': body,
                }            
                sms = self.env['sms.sms'].sudo().create(vals)
                return {
                    'message' : 'success'
                }
            else:
                return {
                    'message' : 'failed'
                }
        


