# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.msegat_sms_gateway_gsc.msegat_sms_gateway_gsc_api.msegat_sms_gateway_gsc_api import MsegatSMSAPI

RESPONSE_STATUES = [
    "Success", "Failed"
]


class MsegatSmsSend(models.Model):
    _name = 'msegat.sms.send'
    _description = "Msegat SMS Send"
    _order = 'id DESC'

    @api.depends('recipients')
    def _compute_total_recipients(self):
        """
            @author: Grow Consultancy Services
        """
        for sms_id in self:
            if sms_id.send_sms_to == "single_contact":
                sms_id.recipients_count = len(sms_id.partner_id)
            elif sms_id.send_sms_to == "multiple_contacts":
                sms_id.recipients_count = len(sms_id.partner_ids)
            elif sms_id.send_sms_to == "sms_group":
                sms_id.recipients_count = len(sms_id.sms_group_id.recipients)
            else:
                sms_id.recipients_count = 0

    def _compute_msegat_response_data(self):
        """
            @author: Grow Consultancy Services
        """
        for sms_id in self:
            sms_id.total_messages = len(sms_id.sms_log_history_ids)
            sms_id.total_successfully_send_messages = len(
                sms_id.sms_log_history_ids.filtered(lambda x: x.status in ["Success"]))
            sms_id.total_error_messages = len(sms_id.sms_log_history_ids.filtered(lambda x: x.status in ["Failed"]))

    SEND_SMS_TO_SELECTIONS = [
        ('single_contact', 'Contact'),
        ('multiple_contacts', 'Multiple Contacts'),
        ('sms_group', 'SMS Group'),
        ('mobile', 'Mobile'),
    ]
    STATUS_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Sent'),
        ('error', 'Error'),
    ]

    name = fields.Char("SMS ID", help="ID", copy=False)
    msegat_account_id = fields.Many2one("msegat.sms.gateway.account", "SMS Account",
                                        domain="[('state', '=', 'confirmed')]", help="SMS Account")
    send_sms_to = fields.Selection(SEND_SMS_TO_SELECTIONS, "Send SMS To", default="single_contact")
    partner_id = fields.Many2one("res.partner", "Contact")
    partner_ids = fields.Many2many("res.partner", "msegat_sms_send_partners_rel", "msegat_sms_send_id", "partner_id",
                                   "Contacts")
    sms_group_id = fields.Many2one("msegat.sms.groups", "SMS Group")
    mobile_number = fields.Char("Mobile (With Country Code)", help="Mobile number (With Country Code)")
    message = fields.Text("Message", help="Message", copy=False)
    recipients_count = fields.Integer(string='recipients Count', compute='_compute_total_recipients')
    recipients = fields.Many2many("res.partner", 'msegat_sms_send_res_partners_rel', 'sms_send_id', 'partner_id',
                                  "Recipients", required=True)
    sms_log_history_ids = fields.One2many("msegat.sms.log.history", "sms_send_rec_id", "SMS Log History")
    state = fields.Selection(STATUS_SELECTION, string="Status", readonly=True, copy=False, default='draft',
                             required=True)
    sms_template_id = fields.Many2one("msegat.sms.template", "SMS Template", domain="[('model_id', '=', False)]",
                                      copy=False, )

    total_messages = fields.Integer("Total No. of Messages", compute="_compute_msegat_response_data")
    total_successfully_send_messages = fields.Integer("Total Successfully Send Messages",
                                                      compute="_compute_msegat_response_data")
    total_error_messages = fields.Integer("Total No. Error Messages", compute="_compute_msegat_response_data")

    # Odoo Logic Section
    # =====================    
    @api.model
    def create(self, vals):
        """
            @author: Grow Consultancy Services
        """
        seq_id = self.env['ir.sequence'].next_by_code('odoo.msegat.sms.send.seq')
        vals.update({'name': seq_id})
        return super(MsegatSmsSend, self).create(vals)

    def unlink(self):
        """
            @author: Grow Consultancy Services
        """
        for rec in self:
            if rec.state == "done":
                error_message = _("You can not delete SMS record which is in Sent State.")
                raise UserError(error_message)

    @api.onchange("sms_template_id")
    def onchange_sms_template_id(self):
        """
            @author: Grow Consultancy Services
        """
        if self.sms_template_id:
            self.message = self.sms_template_id.message
        else:
            self.message = ""

    def action_view_recipients(self):
        """
            @author: Grow Consultancy Services
            @return: action or error
        """
        recipients = []
        if self.send_sms_to == "single_contact":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.partner_id.ids)])
        elif self.send_sms_to == "multiple_contacts":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.partner_ids.ids)])
        elif self.send_sms_to == "sms_group":
            recipients = self.env['res.partner'].sudo().search([('id', 'in', self.sms_group_id.recipients.ids)])

        action = {
            'domain': "[('id', 'in', " + str(recipients.ids) + " )]",
            'name': "Recipients",
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
        }
        return action

    def create_sent_sms_log(self, msegat_account_id, datas, CustomStatusCode, ErrorOrSuccessDict):
        """
            @author: Grow Consultancy Services
        """
        log_status = ""
        if CustomStatusCode == 200:
            log_status = "Success"
        else:
            log_status = "Failed"

        msegat_sms_log_history_obj = self.env['msegat.sms.log.history']
        msegat_sms_log_history_obj.create({
            "sms_send_rec_id": self.id,
            "msegat_account_id": msegat_account_id.id,
            "mobile_number": datas.get("mobile_number"),
            "message": datas.get("message"),
            "status": log_status,
            "error_code": ErrorOrSuccessDict.get("error_code"),
            "error_message": ErrorOrSuccessDict.get("error_message"),
            "error_status_code": ErrorOrSuccessDict.get("error_status_code"),
        })
        return True

    def action_send_sms_to_recipients(self):
        """
            @author: Grow Consultancy Services
        """
        msegat_account_id = self.msegat_account_id
        send_sms_to = self.send_sms_to

        error_message = ""
        if not msegat_account_id:
            error_message = _("SMS Account is required so select Account and try again to Send Message.")
            raise UserError(error_message)
        if not send_sms_to:
            error_message = _("Send SMS To is required so select Send SMS To and try again to Send Message.")
            raise UserError(error_message)

        MsegatSMSAPIObj = MsegatSMSAPI()
        message = self.message

        if self.send_sms_to == "single_contact":
            if not self.partner_id.mobile:
                raise ValidationError(_("Please assign Mobile number to the {}".format(self.partner_id.name)))
            datas = {
                'message': message,
                'mobile_number': "%s" % ((self.partner_id.mobile or "").replace(" ", ""))
            }
            CustomStatusCode, ErrorOrSuccessDict = MsegatSMSAPIObj.post_msegat_sms_send_to_recipients_api(
                msegat_account_id, datas)
            self.create_sent_sms_log(msegat_account_id, datas, CustomStatusCode, ErrorOrSuccessDict)
        elif self.send_sms_to == "multiple_contacts":
            not_set_mobile_partners = self.partner_ids.filtered(lambda x: not x.mobile)
            if not_set_mobile_partners:
                raise ValidationError(
                    _("Please assign Mobile number to the\n\n {}".format(self.partner_ids.mapped("name"))))
            for partner_id in self.partner_ids:
                datas = {
                    'message': message,
                    'mobile_number': "%s" % ((partner_id.mobile or "").replace(" ", ""))
                }
                CustomStatusCode, ErrorOrSuccessDict = MsegatSMSAPIObj.post_msegat_sms_send_to_recipients_api(
                    msegat_account_id, datas)
                self.create_sent_sms_log(msegat_account_id, datas, CustomStatusCode, ErrorOrSuccessDict)
        elif self.send_sms_to == "sms_group":
            not_set_mobile_partners = self.sms_group_id.recipients.filtered(lambda x: not x.mobile)
            if not_set_mobile_partners:
                raise ValidationError(
                    _("Please assign Mobile number to the\n\n {}".format(self.partner_ids.mapped("name"))))
            for partner_id in self.sms_group_id.recipients:
                datas = {
                    'message': message,
                    'mobile_number': "%s" % ((partner_id.mobile or "").replace(" ", ""))
                }
                CustomStatusCode, ErrorOrSuccessDict = MsegatSMSAPIObj.post_msegat_sms_send_to_recipients_api(
                    msegat_account_id, datas)
                self.create_sent_sms_log(msegat_account_id, datas, CustomStatusCode, ErrorOrSuccessDict)
        elif self.mobile_number:
            datas = {
                'message': message,
                'mobile_number': "%s" % ((self.mobile_number or "").replace(" ", ""))
            }
            CustomStatusCode, ErrorOrSuccessDict = MsegatSMSAPIObj.post_msegat_sms_send_to_recipients_api(
                msegat_account_id, datas)
            self.create_sent_sms_log(msegat_account_id, datas, CustomStatusCode, ErrorOrSuccessDict)

        if self.total_messages == self.total_error_messages:
            self.write({
                'state': 'error',
            })
        else:
            self.write({
                'state': 'done',
            })
        return True
