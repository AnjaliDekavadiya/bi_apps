# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class ParkingBookingWizard(models.TransientModel):
    _name = 'sh.parking.booking.wizard'
    _description = 'Parking Booking Wizard'

    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="Member Customer Name", required=True, domain="[('sh_is_memeber', '=', True)]")
    sh_vehicle_id = fields.Many2one(
        comodel_name="sh.parking.vehicle", string="Vehicle Type")
    sh_vehicle_no = fields.Char(string="Vehicle no", required=True)
    sh_amount = fields.Float(
        string='Amount', compute='_compute_sh_amount_price')
    payment_datetime = fields.Datetime(
        string="Payment Date",  default=datetime.today())
    sh_slot_id = fields.Many2one(
        comodel_name='sh.parking.slot', string='Slot Name')
    sh_subslot_id = fields.Many2one(
        comodel_name='sh.parking.subslot', string='Slot Name')
    sh_duration = fields.Float(string="Duration")
    barcode = fields.Char(
        string="Card No.", help="ID used for Member identification.", copy=False)
    sh_membership_id = fields.Many2one(
        comodel_name='sh.parking.membership', string='Membership Name')
    sh_journal_id = fields.Many2one(
        comodel_name="account.journal", string="Paid Payment Journal", related='company_id.sh_journal_id', readonly=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, default=lambda self: self.env.company)
    sh_is_memeber = fields.Boolean(string="is Member")
    sh_expected_check_out_time = fields.Datetime(
        string="Expected Check out date time")
    is_print = fields.Boolean(string="is Member", default=True)

    qr_code_no = fields.Char(string='Qr no.')

    @api.model
    def default_get(self, fields):
        rec = super(ParkingBookingWizard, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        subslot = self.env['sh.parking.subslot'].browse(res_ids)
        if subslot:
            rec.update(
                partner_id=subslot.sh_slot_id.company_id.sh_default_user,
                sh_vehicle_id=subslot.sh_slot_id.sh_vehicle_id,
                sh_slot_id=subslot.sh_slot_id,
                sh_subslot_id=subslot.id,
                sh_journal_id=subslot.sh_slot_id.company_id.sh_journal_id,
                sh_is_memeber=subslot.sh_slot_id.company_id.sh_default_user.sh_is_memeber,
                payment_datetime=datetime.today(),
            )
        return rec

    @api.onchange('partner_id')
    def onchange_partner_id_booking(self):
        if self.partner_id:
            self.sh_is_memeber = self.partner_id.sh_is_memeber

    # Select Membership From card number
    @api.onchange('barcode', 'sh_membership_id')
    def onchange_barcode(self):
        if self.barcode:
            membership = self.env['sh.parking.membership'].search([
                ('barcode', '=', self.barcode)
            ], limit=1)
            if membership:
                self.partner_id = membership.partner_id.id
                self.sh_membership_id = membership.id
            else:
                raise UserError(
                    'No Membership Found...')

    # Calculate Price for parking
    @api.depends('sh_duration')
    def _compute_sh_amount_price(self):
        for rec in self:
            rec.sh_amount = 0
            if rec.sh_duration:
                if rec.sh_slot_id.sh_slot_time == 'days':
                    duration = rec.sh_duration/24
                    rec.sh_amount = rec.sh_slot_id.sh_charges*duration
                elif rec.sh_slot_id.sh_slot_time == 'hours':
                    rec.sh_amount = rec.sh_slot_id.sh_charges*rec.sh_duration
                else:
                    duration = rec.sh_duration*60
                    rec.sh_amount = rec.sh_slot_id.sh_charges*duration

    # Print Receipt for Walking Customer
    def make_customer_payment_receipt(self):
        if self.sh_is_memeber == False:
            self.sh_subslot_id.sh_parking_indication = False
            self.sh_expected_check_out_time = self.payment_datetime + \
                relativedelta(hours=self.sh_duration)
            payment_id = self.env['account.payment'].sudo().create({
                'payment_type': 'inbound',
                'partner_id': self.partner_id.id,
                'amount': self.sh_amount,
                'date': fields.Date.today(),
                'ref': self.sh_subslot_id.name,
                'journal_id': self.sh_journal_id.id,
                # 'payment_method_line_id': self.payment_method_line_id.id,
            })
            payment_id.action_post()
            history_id = self.env['sh.parking.history'].sudo().create({
                'sh_subslot_id': self.sh_subslot_id.id,
                'sh_partner_id': self.partner_id.id,
                'sh_vehicle_id': self.sh_vehicle_id.id,
                'sh_check_in_time': datetime.today(),
                'sh_duration': self.sh_duration,
                'sh_vehicle_no': self.sh_vehicle_no,
                'sh_expected_check_out_time': self.sh_expected_check_out_time,
                'sh_amount': self.sh_amount,
            })
            history_id.name = self.env['ir.sequence'].next_by_code(
                'sh.parking.qrcode_no')
            self.qr_code_no = history_id.name
            self.sh_subslot_id.qr_code_no = history_id.name
            datas = self.read()[0]

            report_action = self.env.ref(
                'sh_parking_mgmt.action_report_sh_parking').report_action([], data=datas)
            report_action['close_on_report_download'] = True
            return report_action

    # Print Receipt for Member
    def make_member_payment_receipt(self):
        if self.barcode and self.partner_id.id == self.sh_membership_id.partner_id.id:
            self.sh_subslot_id.sh_parking_indication = False
            self.sh_expected_check_out_time = datetime.today() + \
                relativedelta(hours=self.sh_duration)
            if self.sudo().sh_membership_id.sh_member_amount_remaining > self.sh_amount:
                self.sudo().sh_membership_id.sh_member_amount_remaining = self.sudo(
                ).sh_membership_id.sh_member_amount_remaining - self.sh_amount
                if self.sudo().sh_membership_id.sh_member_amount_remaining < self.company_id.sh_remaining_amount:
                    template_id = self.env.ref(
                        'sh_parking_mgmt.sh_parking_mgmt_member_email')
                    template_id.sudo().send_mail(self.id, force_send=True)
                history_id = self.env['sh.parking.history'].sudo().create({
                    'sh_subslot_id': self.sh_subslot_id.id,
                    'sh_partner_id': self.partner_id.id,
                    'sh_vehicle_id': self.sh_vehicle_id.id,
                    'sh_check_in_time': datetime.today(),
                    'sh_duration': self.sh_duration,
                    'sh_vehicle_no': self.sh_vehicle_no,
                    'sh_expected_check_out_time': self.sh_expected_check_out_time,
                    'sh_membership_id': self.sudo().sh_membership_id.id,
                    'sh_amount': self.sh_amount,
                })
                history_id.name = self.env['ir.sequence'].next_by_code(
                    'sh.parking.qrcode_no')
                self.qr_code_no = history_id.name
                self.sh_subslot_id.qr_code_no = history_id.name
                datas = self.read()[0]
                report_action = self.env.ref(
                    'sh_parking_mgmt.action_report_sh_parking').report_action([], data=datas)
                report_action['close_on_report_download'] = True
                return report_action
            else:
                if self.sudo().sh_membership_id.sh_member_amount_remaining < self.sh_amount:
                    raise UserError(
                        'Please recharge your Membership Wallet...')
                return {'type': 'ir.actions.act_window_close'}
        else:
            raise UserError('Membership not found...')
