from odoo import models
from odoo.exceptions import UserError
from odoo.exceptions import AccessError
import logging
import requests
import threading
import uuid

from odoo import exceptions, _

_logger = logging.getLogger(__name__)

DEFAULT_OLG_ENDPOINT = 'https://olg.api.odoo.com'


class AutoCompleter(models.Model):
    _name = 'ai.autocompleter'

    def generate_text_olg_api(self, prompt, conversation_history=[]):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            olg_api_endpoint = IrConfigParameter.get_param('web_editor.olg_api_endpoint', DEFAULT_OLG_ENDPOINT)
            response = self.iap_jsonrpc(olg_api_endpoint + "/api/olg/1/chat", params={
                'prompt': prompt,
                'conversation_history': conversation_history or [],
                'version': "17.0",
            }, timeout=30)
            if response['status'] == 'success':
                return response['content']
            elif response['status'] == 'error_prompt_too_long':
                raise UserError(_("Sorry, your prompt is too long. Try to say it in fewer words."))
            else:
                raise UserError(_("Sorry, we could not generate a response. Please try again later."))
        except AccessError:
            raise AccessError(_("Oops, it looks like our AI is unreachable!"))

    def iap_jsonrpc(self, url, method='call', params=None, timeout=15):
        """
        Calls the provided JSON-RPC endpoint, unwraps the result and
        returns JSON-RPC errors as exceptions.
        """
        if hasattr(threading.current_thread(), 'testing') and threading.current_thread().testing:
            raise exceptions.AccessError("Unavailable during tests.")

        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': uuid.uuid4().hex,
        }

        _logger.info('iap jsonrpc %s', url)
        try:
            req = requests.post(url, json=payload, timeout=timeout)
            req.raise_for_status()
            response = req.json()
            _logger.info("iap jsonrpc %s answered in %s seconds", url, req.elapsed.total_seconds())
            if 'error' in response:
                name = response['error']['data'].get('name').rpartition('.')[-1]
                message = response['error']['data'].get('message')
                if name == 'InsufficientCreditError':
                    e_class = InsufficientCreditError
                elif name == 'AccessError':
                    e_class = exceptions.AccessError
                elif name == 'UserError':
                    e_class = exceptions.UserError
                else:
                    raise requests.exceptions.ConnectionError()
                e = e_class(message)
                e.data = response['error']['data']
                raise e
            return response.get('result')
        except (
                ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError) as e:
            raise exceptions.AccessError(
                _('The url that this service requested returned an error. Please contact the author of the app. The url it tried to contact was %s',
                  url)
            )


class InsufficientCreditError(Exception):
    pass