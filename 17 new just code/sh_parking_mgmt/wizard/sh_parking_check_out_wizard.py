# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models,_
from datetime import datetime


class Parkingcheck_outWizard(models.TransientModel):
    _name = 'sh.parking.check_out.wizard'
    _description = 'Parking Check-Out Wizard'
    qr_code_no = fields.Char(string='Qr no.')
    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="Member Customer Name")
    sh_subslot_id = fields.Many2one(
        comodel_name='sh.parking.subslot', string='Slot Name')
    sh_vehicle_id = fields.Many2one(
        comodel_name="sh.parking.vehicle", string="Vehicle Type")
    sh_vehicle_no = fields.Char(string="Vehicle no")

    sh_check_in_time = fields.Datetime(
        string="Check in date time")
    sh_check_out_time = fields.Datetime(
        string="Check out date time", default=datetime.today())
    sh_duration = fields.Float(string=" Extra Duration")
    sh_journal_id = fields.Many2one(
        comodel_name="account.journal", string="Paid Payment Journal", related='company_id.sh_journal_id', readonly=False)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 required=True, default=lambda self: self.env.company)

    late_charge = fields.Float(string="late Charge")
    is_want_payment = fields.Boolean(string="is want payment")

    def make_check_out(self):
        payment_id = self.env['account.payment'].sudo().create({
            'payment_type': 'inbound',
            'partner_id': self.partner_id.id,
            'amount': self.late_charge,
            'date': fields.Date.today(),
            'ref': self.sh_subslot_id.name,
            'journal_id': self.sh_journal_id.id,
        })
        payment_id.action_post()
        self.sh_subslot_id.qr_code_no = False
        self.sh_subslot_id.sh_parking_indication = True
        record = self.env['sh.parking.history'].search([
            ('name', '=', self.qr_code_no)
        ], limit=1)
        record.sh_check_out_time = self.sh_check_out_time
        notifications = []
        message = _("Check Out Successfully...")
        notifications.append(
            (self.env.user.partner_id, 'simple_notification',
             {'title': _('Checked Out '), 'message':  message, 'warning': True}))
        self.env['bus.bus']._sendmany(notifications)
