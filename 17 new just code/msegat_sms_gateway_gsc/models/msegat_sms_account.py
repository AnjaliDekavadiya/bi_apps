# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons.msegat_sms_gateway_gsc.msegat_sms_gateway_gsc_api.msegat_sms_gateway_gsc_api import MsegatSMSAPI


class MsegatSmsGatewayAccount(models.Model):
    _name = 'msegat.sms.gateway.account'
    _description = "Msegat SMS Gateway SMS"

    def _compute_total_sms_data(self):
        msegat_sms_send_obj = self.env['msegat.sms.send']
        msegat_sms_log_history_obj = self.env['msegat.sms.log.history']
        for msegat_account in self:
            msegat_account.sms_records_count = len(msegat_sms_send_obj.search([
                ('msegat_account_id', '=', msegat_account.id)]))
            msegat_account.account_sms_logs_count = len(msegat_sms_log_history_obj.search([
                ('msegat_account_id', '=', msegat_account.id)]))

    name = fields.Char("Account Name", required=True, copy=False, help="Msegat account name")
    username = fields.Char("User Name", required=True, copy=False, help="User name", )
    api_key = fields.Char("API Key", required=True, copy=False, help="API Key")
    msegat_sender_id = fields.Many2one("msegat.account.sender.ids", "Sender ID/TAG Name", copy=False,
                                       help="Sender ID / TAG Name")
    test_connection_mobile_number = fields.Char("Test Connection Mobile Number",
                                                help="Mobile number should be with country code i.e +91xxxxxxxx")
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
    ], default='new', help="State")
    msegat_current_balance = fields.Char("Msegat Current Balance", help="Remaining amount in Msegat")
    is_default_sms_account = fields.Boolean("Is Default SMS Account?", copy=False)

    # Advanced Features
    is_confirm_so_to_send_sms = fields.Boolean("Confirm Order to Send SMS?", default=False, copy=False)
    sms_so_confirm_template_id = fields.Many2one("msegat.sms.template", "SMS Template",
                                                 domain="[('model_id', '!=', False), \
                                                 ('model_id.model', '=', 'sale.order')]", copy=False)
    is_validate_do_to_send_sms = fields.Boolean("Validate Delivery to Send SMS?", default=False, copy=False)
    sms_do_validate_template_id = fields.Many2one("msegat.sms.template", "SMS Template",
                                                  domain="[('model_id', '!=', False), \
                                                  ('model_id.model', '=', 'stock.picking')]", copy=False)

    # Magic button's fields
    sms_records_count = fields.Integer(string='Account SMS Records Count', compute='_compute_total_sms_data')
    account_sms_logs_count = fields.Integer(string='Account SMS Logs Count', compute='_compute_total_sms_data')

    def reset_to_new(self):
        for sms_account in self:
            sms_account.write({'state': 'new'})
        return True

    def action_open_sms_send_records(self):
        """
            @author: Grow Consultancy Services
            @return: action or error
        """
        send_sms_records = self.env['msegat.sms.send'].sudo().search([('msegat_account_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(send_sms_records.ids) + " )]",
            'name': "Send SMS Records",
            'view_mode': 'tree,form',
            'res_model': 'msegat.sms.send',
            'type': 'ir.actions.act_window',
        }
        return action

    def action_open_sms_account_logs_records(self):
        """
            @author: Grow Consultancy Services
            @return: action or error
        """
        account_sms_logs_records = self.env['msegat.sms.log.history'].sudo().search([
            ('msegat_account_id', '=', self.id)])
        action = {
            'domain': "[('id', 'in', " + str(account_sms_logs_records.ids) + " )]",
            'name': "SMS Logs History",
            'view_mode': 'tree,form',
            'res_model': 'msegat.sms.log.history',
            'type': 'ir.actions.act_window',
        }
        return action

    # API Logic Section
    # =====================
    def test_msegat_sms_connection(self):
        """
            @author: Grow Consultancy Services
        """
        MsegatSMSAPIObj = MsegatSMSAPI()
        response_obj, response_flag = MsegatSMSAPIObj.test_msegat_sms_connection_api(self)
        if response_flag:
            self.msegat_current_balance = response_obj.text
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': _("Service working properly!!! You're successfully connected with Msegat."),
                    'img_url': '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        else:
            error_msg = _("Something went to wrong!!!.\nResponse Status Code: %s\nResponse Error: %s" % (
                response_obj.status_code, response_obj.text))
            raise UserError(error_msg)

    def test_and_confirm_msegat_sms_account(self):
        """
            @author: Grow Consultancy Services
        """
        if not self.msegat_sender_id:
            error_msg = _("Please first set Sender ID/Tag Name and try again to confirm account.")
            raise ValidationError(error_msg)
        resp = self.test_msegat_sms_connection()
        self.state = "confirmed"
        return resp

    def get_msegat_account_balance(self):
        """
            @author: Grow Consultancy Services
        """
        self.test_msegat_sms_connection()
        return True

    def test_msegat_send_sms_connection(self):
        """
            @author: Grow Consultancy Services
        """
        if not self.test_connection_mobile_number:
            raise UserError(_("'Test Connection Mobile Number' is required for connection checking!!!"))

        MsegatSMSAPIObj = MsegatSMSAPI()
        response_obj, response_flag = MsegatSMSAPIObj.test_msegat_send_sms_connection_api(self)
        if response_flag:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': _("Service working properly!!! Your message sent successfully to %s" % (
                        self.test_connection_mobile_number)),
                    'img_url': '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        else:
            error_msg = _("Something went to wrong!!!.\nResponse Status Code: %s\nResponse Error: %s" % (
                response_obj.status_code, response_obj.text))
            raise UserError(error_msg)

    def fetch_msegat_account_sender_ids_or_tags_name(self):
        """
            @author: Grow Consultancy Services
        """
        MsegatSMSAPIObj = MsegatSMSAPI()
        response, response_flag = MsegatSMSAPIObj.fetch_msegat_account_sender_ids_or_tags_name_api(self)
        if response_flag:
            msegat_account_sender_ids_obj = self.env['msegat.account.sender.ids']
            for sender_id_dict in response:
                sender_id = sender_id_dict.get("SenderID")
                sender_id_status = sender_id_dict.get("Status")
                existing_send_id = msegat_account_sender_ids_obj.search([("sender_id", "=ilike", sender_id)], limit=1)
                if existing_send_id:
                    existing_send_id.status = sender_id_status
                else:
                    msegat_account_sender_ids_obj.create({
                        "sender_id": sender_id,
                        "status": sender_id_status
                    })

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': _("Successfully retrieved Sender ID/TAG Name from Msegat..."),
                    'img_url': '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        return True

    def create_sent_sms_log(self, send_sms_id, datas, CustomStatusCode, ErrorOrSuccessDict):
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
            "sms_send_rec_id": send_sms_id and send_sms_id.id or False,
            "msegat_account_id": self.id,
            "mobile_number": datas.get("mobile_number"),
            "message": datas.get("message"),
            "status": log_status,
            "sale_order_id": datas.get("sale_order_id"),
            "picking_id": datas.get("picking_id"),
            "error_code": ErrorOrSuccessDict.get("error_code"),
            "error_message": ErrorOrSuccessDict.get("error_message"),
            "error_status_code": ErrorOrSuccessDict.get("error_status_code"),
        })
        return True
