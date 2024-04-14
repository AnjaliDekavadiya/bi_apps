# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class HmsAppointment(models.Model):
    _inherit = 'hms.appointment'

    @api.model
    def send_appointment_reminder(self):
        reminder_appointments = super(HmsAppointment, self).send_appointment_reminder()
        for rec in reminder_appointments:
            sms_template = rec.company_id.acs_reminder_sms_template_id
            if rec and rec.patient_id and rec.patient_id.mobile and sms_template:
                rec._message_sms_with_template(
                    template=sms_template,
                    template_fallback=_("Dear %(name)s, Reminder for your appointment %(number)s at %(hospital)s.", name=rec.patient_id.name, number=rec.name, hospital=rec.sudo().company_id.name),
                    partner_ids=[rec.id],
                    put_in_queue=False
                )
        return reminder_appointments

    def appointment_confirm(self):
        res = super(HmsAppointment, self).appointment_confirm()
        for rec in self:
            template = rec.sudo().company_id.appointment_registartion_sms_template_id
            if template and rec.patient_id and rec.patient_id.mobile:
                rec._message_sms_with_template(
                    template=template,
                    template_fallback=_("Dear %(name)s, your appointment %(number)s registartion number is confirmed at %(hospital)s.", name=rec.patient_id.name, number=rec.name, hospital=rec.sudo().company_id.name),
                    partner_ids=[rec.id],
                    put_in_queue=False
                )
                
        return res


class HmsPatient(models.Model):
    _inherit = 'hms.patient'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            company_id = record.sudo().company_id or self.env.user.sudo().company_id
            if company_id.patient_registartion_sms_template_id:
                record._message_sms_with_template(
                    template=company_id.patient_registartion_sms_template_id,
                    template_fallback=_("Dear %(name)s, Your Patient Registration No. is: %(code)s in %(hospital)s.", name=record.name, code=record.code, hospital=company_id.name),
                    partner_ids=[record.id],
                    put_in_queue=False
                )
        return res

    def action_send_otp_sms(self):
        return self.partner_id.action_send_otp_sms()

    def action_verify_otp_sms(self):
        return self.partner_id.action_verify_otp_sms()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: