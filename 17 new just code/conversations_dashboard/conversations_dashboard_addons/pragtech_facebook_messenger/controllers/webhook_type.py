from odoo import api, http, SUPERUSER_ID, _, modules
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo import registry as registry_get
import requests
import base64


class WebhookType(http.Controller):
    def get_webhook_type(self):
        webhook_verified = request.env['ir.config_parameter'].sudo().get_param('pragtech_facebook_messenger.webhook_verified')
        if webhook_verified:
            return 'json'
        else:
            return 'http'
