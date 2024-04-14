from odoo import http
from odoo.http import request
import json


class Main(http.Controller):

    @http.route(['/send_discount_otp_message'], type="json", auth='public', methods=['POST'], csrf=False)
    def send_discount_otp_message(self):
        # TODO::- send message to whatsapp template method
        otp_contact_id = request.env['ir.config_parameter'].sudo().get_param(
            'dr_discount_otp_auth.contact_id')
        otp_whatsapp_template_id = request.env['ir.config_parameter'].sudo().get_param(
            'dr_discount_otp_auth.whatsapp_template_id')


        contact_object = request.env["res.users"].sudo().search([('id', '=', int(otp_contact_id))], limit=1)
        contact_phone_number = contact_object.phone

        data = json.loads(request.httprequest.data)
        otp_body = data['params']["otpBody"]
        wamid = ""

        try:
            # Check if any parameter is false or not founded.
            if not otp_whatsapp_template_id:
                return {"wamid", wamid}

            wamids = request.env["whatsapp.message"].sudo().send_message([contact_phone_number], otp_whatsapp_template_id, otp_body)
            wamid = wamids[0]
        except Exception as e:
            print(e)

        return {"wamid": wamid}
