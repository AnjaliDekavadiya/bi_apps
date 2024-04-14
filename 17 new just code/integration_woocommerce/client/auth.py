# See LICENSE file for full copyright and licensing details.

from time import time
from random import randint
from hmac import new as HMAC
from hashlib import sha1, sha256
from base64 import b64encode
from collections import OrderedDict
from urllib.parse import urlencode, quote, unquote, parse_qsl, urlparse

from requests.auth import HTTPBasicAuth

try:
    from aiohttp import BasicAuth
except (ImportError, IOError) as ex:
    import logging
    _logger = logging.getLogger(__name__)
    _logger.error(ex)


class Auth(object):
    """ Boilerplate for handling authentication stuff. """
    def __init__(self, **kwargs):
        self.consumer_key = kwargs.get('consumer_key')
        self.consumer_secret = kwargs.get('consumer_secret')
        self.wp_user = kwargs.get('wp_user', None)
        self.wp_pass = kwargs.get('wp_app_password', None)
        self.query_string_auth = kwargs.get('query_string_auth', False)

    def get_auth_url(self, endpoint_url, method, params):
        """ Returns the URL with added Auth params """
        result = self.build_url(endpoint_url, params)
        return result

    def get_auth(self):
        """ Returns the auth parameter used in requests """
        return False

    @staticmethod
    def parse_url(endpoint_url):
        params = OrderedDict()

        if "?" in endpoint_url:
            url = endpoint_url[:endpoint_url.find("?")]
            for key, value in parse_qsl(urlparse(endpoint_url).query):
                params[key] = value
        else:
            url = endpoint_url

        return url, params

    @staticmethod
    def build_url(url, params):
        query_string = urlencode(params)

        if query_string:
            return f"{url}?{query_string}"

        return url


class SyncBasicAuth(Auth):

    def get_auth_url(self, endpoint_url, method, params):
        if self.query_string_auth:
            url, req_params = self.parse_url(endpoint_url)
            req_params.update(params)
            req_params['consumer_key'] = self.consumer_key
            req_params['consumer_secret'] = self.consumer_secret

            result = self.build_url(url, req_params)
            return result

        result = super(SyncBasicAuth, self).get_auth_url(endpoint_url, method, params)
        return result

    def get_auth(self):
        if self.wp_user:
            return HTTPBasicAuth(self.wp_user, self.wp_pass)
        if not self.query_string_auth:
            return HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        return super().get_auth()


class AsyncBasicAuth(SyncBasicAuth):
    def get_auth(self):
        if self.wp_user:
            return BasicAuth(self.wp_user, self.wp_pass)
        if not self.query_string_auth:
            return BasicAuth(self.consumer_key, self.consumer_secret)
        return super().get_auth()


class OAuth(Auth):
    """ API Class """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.version = kwargs.get('version', 'v3')
        self.timestamp = int(time())

    def get_auth_url(self, endpoint_url, method, params):
        """ Returns the URL with OAuth params """
        url, req_params = self.parse_url(endpoint_url)

        req_params.update(params)

        req_params['oauth_nonce'] = self.generate_nonce()
        req_params['oauth_timestamp'] = int(time())
        req_params['oauth_version'] = '1.0'
        req_params['oauth_signature_method'] = 'HMAC-SHA256'
        req_params['oauth_consumer_key'] = self.consumer_key
        req_params['oauth_signature'] = self.generate_oauth_signature(req_params, url, method)

        return self.build_url(url, req_params)

    def generate_oauth_signature(self, params, url, method):
        """ Generate OAuth Signature """
        if 'oauth_signature' in params.keys():
            del params['oauth_signature']

        base_request_uri = quote(url, '')

        params = self.sorted_params(params)
        params = self.normalize_parameters(params)
        query_params = ['{param_key}%3D{param_value}'.format(param_key=key, param_value=value)
                        for key, value in params.items()]

        query_string = '%26'.join(query_params)
        string_to_sign = f'{method}&{base_request_uri}&{query_string}'

        consumer_secret = str(self.consumer_secret)
        if self.version not in ['v1', 'v2']:
            consumer_secret += '&'

        hash_signature = HMAC(
            consumer_secret.encode(),
            str(string_to_sign).encode(),
            sha256
        ).digest()

        return b64encode(hash_signature).decode('utf-8').replace('\n', '')

    @staticmethod
    def sorted_params(params):
        ordered = OrderedDict()
        base_keys = sorted(set(k.split('[')[0] for k in params.keys()))

        for base in base_keys:
            for key in params.keys():
                if key == base or key.startswith(base + '['):
                    ordered[key] = params[key]

        return ordered

    @staticmethod
    def normalize_parameters(params):
        """ Normalize parameters """
        params = params or {}
        normalized_parameters = OrderedDict()

        def get_value_like_as_php(val):
            """ Prepare value for quote """
            base = (str, bytes)

            if isinstance(val, base):
                return val
            elif isinstance(val, bool):
                return '1' if val else ''
            elif isinstance(val, int):
                return str(val)
            elif isinstance(val, float):
                return str(int(val)) if val % 1 == 0 else str(val)
            else:
                return ""

        for key, value in params.items():
            value = get_value_like_as_php(value)
            key = quote(unquote(str(key))).replace('%', '%25')
            value = quote(unquote(str(value))).replace('%', '%25')
            normalized_parameters[key] = value

        return normalized_parameters

    @staticmethod
    def generate_nonce():
        """ Generate nonce number """
        nonce = ''.join([str(randint(0, 9)) for i in range(8)])
        return HMAC(
            nonce.encode(),
            'secret'.encode(),
            sha1
        ).hexdigest()
