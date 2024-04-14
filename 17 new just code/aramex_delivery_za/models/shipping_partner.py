import base64
import json
import requests
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools import file_path


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('aramex_ts', 'Aramex')])
    am_user_name = fields.Char("Email/Username")
    am_password = fields.Char("Password")
    am_account_number = fields.Char("Account Number")

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'aramex_ts':
            image_path = file_path('aramex_delivery_za/static/description/icon.png')
            self.image = base64.b64encode(open(image_path, 'rb').read())
        return res

    @api.model
    def _aramex_send_request(self, request_url, request_data, prod_environment=True, method='GET'):
        log_obj = self.env['shipping.api.log']
        headers = {
            'Content-Type': 'application/json',
        }
        data = json.dumps(request_data)
        api_url = "https://nservice.aramex.co.za/Json/JsonV1/" + request_url
        if not prod_environment:
            raise UserError(_("Sandbox/Test environment isn't available. Please switch environment of delivery method."))
        try:
            req = requests.request(method, api_url, headers=headers, data=data)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                req = req.content.decode("utf-8")
                response = json.loads(req)
            else:
                response = json.loads(req.content)
        except requests.HTTPError as e:
            raise UserError("%s" % req.text)
        log_obj.sudo().create({'shipping_partner_id': self.id, 'user_id': self.env.user.id, 'request_url': api_url, 'request_data': request_data, 'response_data': response})
        return response
