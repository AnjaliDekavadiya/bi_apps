from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError
import json
import requests

_logger = logging.getLogger("RO DPD")


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_dpd_shipping_provider = fields.Boolean(string="Is Use DPD Shipping Provider",
                                               help="True when we need to use dpd shipping provider",
                                               default=False, copy=False)
    dpd_api_url = fields.Char(string='DPD API URL',
                              default="https://api.dpd.ro/v1",
                              help="Get URL details from DPD")
    username = fields.Char(string='Username',
                           help="This parameter is the Username Given By DPD")
    password = fields.Char(string='Password',
                           help="Please Enter Valid Password Which Is Given By DPD")

    def get_dpd_api_calling(self, api_url=False):
        data = {
            "userName": self.username,
            "password": self.password
        }
        data = json.dumps(data)
        headers = {
            'Content-Type': 'application/json'}
        try:
            response_body = requests.request(method="POST", url=api_url, headers=headers,data=data)
            if response_body.status_code in [200, 201]:
                _logger.info("RO DPD ResponseData : {}".format(response_body.json()))
                return response_body.json()
            else:
                raise ValidationError(response_body.content)
        except Exception as e:
            raise ValidationError(e)

    def get_dpd_services(self):
        """this method is used for get all services from dpd"""
        api_url = "{}/services".format(self.dpd_api_url)
        try:
            response_data = self.get_dpd_api_calling(api_url)
            for response in response_data.get('services'):
                if not self.env['dpd.services'].search([('name', '=', response.get('name'))]):
                    couriers = {'service_id': response.get('id'),
                                'name': response.get('name')}
                    self.env['dpd.services'].create(couriers)
                    _logger.info("{} Service Create".format(response.get('type')))
        except Exception as e:
            raise ValidationError(e)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Yeah! DPD Romania Providers Imported successfully.",
                'img_url': '/web/static/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
