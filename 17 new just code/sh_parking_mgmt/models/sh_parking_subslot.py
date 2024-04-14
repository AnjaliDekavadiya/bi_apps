# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from datetime import datetime
from odoo import fields, models, _, api
from odoo.exceptions import UserError


class Subslot(models.Model):

    _name = 'sh.parking.subslot'
    _description = 'Parking Subslot'

    name = fields.Char(string='Subslot Name', required=True,
                       readonly=True, default=lambda self: _('New'),copy=False)
    sh_slot_id = fields.Many2one(
        comodel_name='sh.parking.slot', string='Slot Name',copy=False)
    sh_parking_indication = fields.Boolean(
        string='Available for parking ?', default=True,copy=False)
    sh_vehicle_id = fields.Many2one(
        comodel_name="sh.parking.vehicle", string="Vehicle",copy=False)
    qr_code_no = fields.Char(string='Qr no.',copy=False)

    
    @api.model
    def calculate_check_out_time(self, qr):
        record = self.env['sh.parking.history'].search([
            ('name', '=', qr)
        ], limit=1)
        if record:
            if record.sh_check_out_time:
                notifications = []
                message = _("Already Check Out ...")
                notifications.append(
                    (self.env.user.partner_id, 'simple_notification',
                     {'title': _('Checked Out '), 'message':  message, 'warning': True}))
                self.env['bus.bus']._sendmany(notifications)
                return {'warning': _("Check Out Successfully... ")}
            else:
                sh_check_out_time = datetime.today()
                if sh_check_out_time <= record.sh_expected_check_out_time:
                    record.sh_subslot_id.sh_parking_indication = True
                    record.sh_check_out_time = sh_check_out_time
                    notifications = []
                    message = _("Check Out Successfully...")
                    notifications.append(
                        (self.env.user.partner_id, 'simple_notification',
                         {'title': _('Checked Out '), 'message':  message, 'warning': True}))
                    self.env['bus.bus']._sendmany(notifications)
                    return {'warning': _("Check Out Successfully... ")}
                else:
                    print("\n\n=================else")
                    charge = record.sh_subslot_id.sh_slot_id.sh_charges
                    late_charge = record.sh_subslot_id.sh_slot_id.sh_late_charges
                    late_duration_time = sh_check_out_time - record.sh_expected_check_out_time
                    late_time = late_duration_time.total_seconds()
                    if record.sh_subslot_id.sh_slot_id.sh_slot_time == 'days':
                        late_time = late_time/(24*3600)
                        late_charge_pay = late_time*charge+late_charge
                    elif record.sh_subslot_id.sh_slot_id.sh_slot_time == 'hours':
                        late_time = late_time/(3600)
                        late_charge_pay = late_time*charge+late_charge
                    else:
                        late_time = late_time/60
                        late_charge_pay = late_time*charge+late_charge
                        
                    print(f"==>> late_charge_pay: {late_charge_pay}")
                    
                    record.sh_amount+=late_charge_pay
                    record.sh_duration = late_duration_time.total_seconds()/3600+record.sh_duration
                    print(f"==>> record.sh_duration: {record.sh_duration}")
                    if record.sh_partner_id.sh_is_memeber == True:
                        if record.sudo().sh_membership_id.sh_member_amount_remaining < record.sh_subslot_id.sh_slot_id.company_id.sh_remaining_amount:
                            template_id = self.env.ref(
                                'sh_parking_mgmt.sh_parking_mgmt_member_check_out_email')
                            template_id.sudo().send_mail(record.id, force_send=True)
                        if record.sudo().sh_membership_id.sh_member_amount_remaining > late_charge_pay:
                            record.sudo().sh_membership_id.sh_member_amount_remaining -= late_charge_pay
                            record.sh_subslot_id.sh_parking_indication = True
                            record.sh_check_out_time = sh_check_out_time
                            notifications = []
                            message = _("Late Amount Charge: %s Deducted From Your Membership:%s" ,round(late_charge_pay, 2),record.sudo().sh_membership_id.name)
                            notifications.append(
                                (self.env.user.partner_id, 'simple_notification',
                                 {'title': _('Checked Out '), 'message':  message, 'warning': True}))
                            self.env['bus.bus']._sendmany(notifications)
                            return {'warning': _("Check Out Successfully... ")}
                        else:
                            notifications = []
                            message = _('Please Recharge Your Membership:%s.\n You should Pay late amount charge:%s',
                                        record.sudo().sh_membership_id.name, round(late_charge_pay, 2))
                            notifications.append(
                                (self.env.user.partner_id, 'simple_notification',
                                 {'title': _('Recharge.. '), 'message':  message}))
                            self.env['bus.bus']._sendmany(notifications)

                        return {'warning': _("Check Out Successfully... ")}
                    else:
                        print("\n\n==================2222222222222 else")
                        wizard_return = {
                            'type': 'ir.actions.act_window',
                            'name': _('Parking Booking Check-Out'),
                            'view_mode': 'form',
                            'res_model': 'sh.parking.check_out.wizard',
                            'target': 'new',
                            'views': [[False, 'form']],
                            'context': {
                                'default_partner_id': record.sh_partner_id.id,
                                'default_qr_code_no': qr,
                                'default_sh_subslot_id': record.sh_subslot_id.id,
                                'default_sh_vehicle_id': record.sh_vehicle_id.id,
                                'default_sh_vehicle_no': record.sh_vehicle_no,
                                'default_sh_check_in_time': record.sh_check_in_time,
                                'default_sh_check_out_time': sh_check_out_time,
                                'default_sh_duration': late_duration_time.total_seconds()/3600,
                                'default_late_charge': late_charge_pay,
                                'default_sh_journal_id': record.sh_subslot_id.sh_slot_id.company_id.sh_journal_id.id,
                            },
                        }
                        print("\n\=====wizard_return",wizard_return)
                        return wizard_return
        else:
            raise UserError(
                'Please Enter Valid Qr-code....')
