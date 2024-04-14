# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests

from odoo import _
from odoo.exceptions import UserError

# API URL Points
MSEGAT_BASE_URL_ENDPOINT = "https://www.msegat.com/gw"
MSEGAT_SEND_SMS_URL_ENDPOINT = MSEGAT_BASE_URL_ENDPOINT + "/sendsms.php"
MSEGAT_GET_ACCOUNT_DETAILS_ENDPOTINT = MSEGAT_BASE_URL_ENDPOINT + "/Credits.php"
MSEGAT_GET_SENDER_TAGS_ENDPOINT = MSEGAT_BASE_URL_ENDPOINT + "/senders.php"

# Success Code
SUCCESS_CODES = {
    '1': "Success",
    'M0000': "Success"
}

# Errors Codes
ERROR_CODES = {
    'M0001': "Variables missing",
    'M0002': "Invalid login info",
    'M0022': "Exceed number of senders allowed",
    'M0023': "Sender Name is active or under activation or refused",
    'M0024': "Sender Name should be in English or number",
    'M0025': "Invalid Sender Name Length",
    'M0026': "Sender Name is already activated or not found",
    'M0027': "Activation Code is not Correct",
    '1010': "Variables missing",
    '1020': "Invalid login info",
    '1050': "MSG body is empty",
    '1060': "Balance is not enough",
    '1061': "MSG duplicated",
    '1064': """Free OTP , Invalid MSG content you should use "Pin Code is: xxxx" or "Verification 
                Code: xxxx" or "رمز التحقق: 1234" , or upgrade your account 
                and activate your sender to send any content""",
    '1110': "Sender name is missing or incorrect",
    '1120': "Mobile numbers is not correct",
    '1140': "MSG length is too long",
    'M0029': """Invalid Sender Name Sender Name should contain only letters, numbers and the maximum length should be 
                11 characters""",
    'M0030': "Sender Name should ended with AD",
    'M0031': "Maximum allowed size of uploaded file is 5 MB",
    'M0032': "Only pdf,png,jpg and jpeg files are allowed!",
    'M0033': "Sender Type should be normal or whitelist only",
    'M0034': "Please Use POST Method",
    'M0036': "There is no any sender"
}


class MsegatSMSAPI():

    def test_msegat_sms_connection_api(self, msegat_account):
        """
            @author: Grow Consultancy Services
        """
        try:
            data = {
                "apiKey": msegat_account.api_key,
                "userName": msegat_account.username,
            }
            data = '''--BOUNDARY
Content-Disposition: form-data; name="userName"

%s
--BOUNDARY
Content-Disposition: form-data; name="apiKey"

%s
--BOUNDARY--''' % (msegat_account.username, msegat_account.api_key)
            headers = {
                'Content-Type': 'multipart/form-data; boundary=BOUNDARY'
            }
            response_obj = requests.post(MSEGAT_GET_ACCOUNT_DETAILS_ENDPOTINT, data=data, headers=headers, timeout=20)
        except Exception as e:
            error_msg = _("Something went wrong while connecting with Msegat.\nRequested URL: %s\nError Message: %s" % (
                MSEGAT_GET_ACCOUNT_DETAILS_ENDPOTINT, e))
            raise UserError(error_msg)

        if response_obj.status_code == 200:
            response = response_obj.text
            try:
                response = float(response)
            except Exception:
                response = response

            if isinstance(response, float):
                return response_obj, True
            elif response in ERROR_CODES:
                ErrorCode = response
                ErrorMessage = ERROR_CODES.get(str(response))
                error_msg = _("Something went wrong while connecting with Msegat.\nRequested URL: %s\nError Code: %s\
                            \nError Message: %s" % (MSEGAT_GET_ACCOUNT_DETAILS_ENDPOTINT, ErrorCode, ErrorMessage))
                raise UserError(error_msg)
        return 0.0, False

    def test_msegat_send_sms_connection_api(self, msegat_account):
        """
            @author: Grow Consultancy Services
        """
        try:
            data = {
                "apiKey": msegat_account.api_key,
                "userName": msegat_account.username,
                "numbers": msegat_account.test_connection_mobile_number,
                "userSender": msegat_account.msegat_sender_id.sender_id,
                "msg": "Your Odoo Msegat successfully connected with Msegat.",
            }
            headers = {
                'Content-Type': 'application/json'
            }
            response_obj = requests.post(MSEGAT_SEND_SMS_URL_ENDPOINT, data=json.dumps(data), headers=headers,
                                         timeout=20)
        except Exception as e:
            error_msg = _("Something went wrong while calling Send SMS API.\nRequested URL: %s\nError Message: %s" % (
                MSEGAT_SEND_SMS_URL_ENDPOINT, e))
            raise UserError(error_msg)

        if response_obj.status_code == 200:
            response = response_obj.json()
            if response.get('code') in SUCCESS_CODES:
                return response_obj, True
            elif response.get('code') in ERROR_CODES:
                ErrorCode = response.get('code')
                ErrorMessage = response.get('message')
                error_msg = _("Something went wrong while calling Send SMS API.\nRequested URL: %s\nError Code: %s\
                                \nError Message: %s" % (MSEGAT_SEND_SMS_URL_ENDPOINT, ErrorCode, ErrorMessage))
                raise UserError(error_msg)
        return False, False

    def fetch_msegat_account_sender_ids_or_tags_name_api(self, msegat_account):
        """
            @author: Grow Consultancy Services
        """
        try:
            data = {
                "apiKey": msegat_account.api_key,
                "userName": msegat_account.username
            }
            headers = {
                'Content-Type': 'application/json'
            }
            response_obj = requests.post(MSEGAT_GET_SENDER_TAGS_ENDPOINT, data=json.dumps(data), headers=headers,
                                         timeout=20)
        except Exception as e:
            error_msg = _("Something went wrong while calling get Sender ID/Tag Name API.\nRequested URL: %s\
                            \nError Message: %s" % (MSEGAT_GET_SENDER_TAGS_ENDPOINT, e))
            raise UserError(error_msg)

        if response_obj.status_code == 200:
            response = response_obj.json()
            if isinstance(response, dict):
                response = [response]
            if isinstance(response, list) and response[0].get('code') in ERROR_CODES:
                ErrorCode = response[0].get('code')
                ErrorMessage = response[0].get('message')
                error_msg = _("Something went wrong while calling get Sender ID/Tag Name API.\nRequested URL: %s\
                            \nError Code: %s\nError Message: %s" % (MSEGAT_SEND_SMS_URL_ENDPOINT,
                                                                    ErrorCode, ErrorMessage))
                raise UserError(error_msg)
            else:
                return response, True
        else:
            ErrorCode = response_obj.status_code
            ErrorMessage = response_obj.text
            error_msg = _("Something went wrong while calling get Sender ID/Tag Name API.\nRequested URL: %s\
                        \nError Code: %s\nError Message: %s" % (MSEGAT_SEND_SMS_URL_ENDPOINT, ErrorCode, ErrorMessage))
            raise UserError(error_msg)
        return {}, False

    def post_msegat_sms_send_to_recipients_api(self, msegat_account, datas):
        """
            @author: Grow Consultancy Services
            @return: CustomStatusCode, ErrorOrSuccessMsg
        """
        try:
            data = {
                "apiKey": msegat_account.api_key,
                "userName": msegat_account.username,
                "numbers": datas.get('mobile_number'),
                "userSender": msegat_account.msegat_sender_id.sender_id,
                "msg": datas.get("message"),
            }
            headers = {
                'Content-Type': 'application/json'
            }
            response_obj = requests.post(MSEGAT_SEND_SMS_URL_ENDPOINT, data=json.dumps(data), headers=headers,
                                         timeout=20)
        except Exception as e:
            error_msg = _("Something went wrong while calling Send SMS API.\nRequested URL: %s\nError Message: %s" % (
                MSEGAT_SEND_SMS_URL_ENDPOINT, e))
            return 404, {'error_code': 404, 'error_message': error_msg, 'error_status_code': 404}

        if response_obj.status_code == 200:
            response = response_obj.json()
            if response.get('code') in SUCCESS_CODES:
                return 200, {}
            elif response.get('code') in ERROR_CODES:
                ErrorCode = response.get('code')
                ErrorMessage = response.get('message')
                error_msg = _("Something went wrong while calling Send SMS API.\nRequested URL: %s\nError Code: %s\
                            \nError Message: %s" % (MSEGAT_SEND_SMS_URL_ENDPOINT, ErrorCode, ErrorMessage))
                return 400, {'error_code': ErrorCode,
                             'error_message': error_msg,
                             'error_status_code': response_obj.status_code}
        return 404, ""
