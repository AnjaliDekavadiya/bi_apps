from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class WebHook(http.Controller):
    @http.route('/hubspot_channel/fetch_hook_data', type='http', auth='public', methods=['POST'], csrf=False)
    def fetch_webhook(self, **post):
        data = json.loads(request.httprequest.data)
