# -*- coding: utf-8 -*-

import pytz
from odoo import models, fields, api, _

# put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]
def _tz_get(self):
    return _tzs

class CustomPosLockPeriod(models.Model):
    _name = "custom.pos.lock.period"
    _inherit = ['mail.thread']
    _description = 'Pos Lock Period'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    period_type = fields.Selection([
        ('time', 'Time Wise'),
        ('date', 'Date Wise'),
        ('datetime', 'Datetime Wise'),
        ('days', 'Days')],
        default="time",
        string="Lock Period Type",
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('activate', 'Activated'),
        ('disable', 'Disabled'),
        ('cancel', 'Canceled')],
        string='Status', 
        readonly=True, 
        copy=False, 
        default='draft',
        tracking=True,
    )
    pos_config_id = fields.Many2one(
        'pos.config',
        string="POS Config",
        required=True,
    )
    close_start_time = fields.Float(
        string="Close Start Time"
    )
    close_end_time = fields.Float(
        string="Close End Time"
    )
    close_start_date = fields.Date(
        string="Close Start Date"
    )
    close_end_date = fields.Date(
        string="Close End Date"
    )
    close_start_datetime = fields.Datetime(
        string="Close Start Datetime"
    )
    close_end_datetime = fields.Datetime(
        string="Close End Datetime"
    )
    close_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),],
        string="Days"
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    allowed_user_ids = fields.Many2many(
        'res.users',
        string="Allowed Users",
        help="These users will not get lock types warning."
    )
    tz = fields.Selection(
        _tz_get, 
        string='Timezone', 
        default=lambda self: self.env.user.tz,
        required=True,
        help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
            "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
            "Anywhere else, time values are computed according to the time offset of your web client."
    )

    created_by_id = fields.Many2one(
        'res.users',
        string="Created by",
        default=lambda self: self.env.user,
        readonly=True,
        copy=False
    )
    created_date = fields.Date(
        string="Created Date",
        default= fields.Date.today(),
        readonly=True,
        copy=False
    )
    approved_by_id = fields.Many2one(
        'res.users',
        string="Approved by",
        readonly=True,
        copy=False 
    )
    approve_date = fields.Date(
        string="Approved Date",
        readonly=True,
        copy=False 
    )
    activate_by_id = fields.Many2one(
        'res.users',
        string="Activated by",
        readonly=True,
        copy=False 
    )
    activate_date = fields.Date(
        string="Activated Date",
        readonly=True,
        copy=False 
    )
    disable_by_id = fields.Many2one(
        'res.users',
        string="Disable by",
        readonly=True,
        copy=False 
    )
    disable_date = fields.Date(
        string="Disable Date",
        readonly=True,
        copy=False 
    )

    @api.onchange('period_type')
    def _onchange_period_type(self):
        self.close_start_time = 0.0
        self.close_end_time = 0.0
        self.close_start_date = False
        self.close_end_date = False
        self.close_start_datetime = False
        self.close_end_datetime = False
        self.close_day = False


    def action_approve_period(self):
        self.ensure_one()
        vals = {
            'state': 'approve',
            'approved_by_id': self.env.user.id,
            'approve_date': fields.Date.today()
        }
        self.write(vals)

    def action_activate_period(self):
        self.ensure_one()
        vals = {
            'state': 'activate',
            'activate_by_id': self.env.user.id,
            'activate_date': fields.Date.today()
        }
        self.write(vals)

    def action_disable_period(self):
        self.ensure_one()
        vals = {
            'state': 'disable',
            'disable_by_id': self.env.user.id,
            'disable_date': fields.Date.today()
        }
        self.write(vals)

    def action_reset_to_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def action_cancel_period(self):
        self.ensure_one()
        self.state = 'cancel'