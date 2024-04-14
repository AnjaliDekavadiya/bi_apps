#  See LICENSE file for full copyright and licensing details.

import logging

from requests import request

from .auth import AsyncBasicAuth, SyncBasicAuth, OAuth


_logger = logging.getLogger(__name__)


class WooCommerceAPI:

    def __init__(self, url, **kwargs):
        self.url = url
        self.wp_api = kwargs.get('wp_api', True)
        self.version = kwargs.get('version', 'wc/v3')
        self.is_ssl = self._is_ssl()
        self.timeout = kwargs.get('timeout', 30)
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.query_string_auth = kwargs.get('query_string_auth', False)
        self.user_agent = kwargs.get('user_agent', 'Odoo-Integration-Woocommerce/1.0')
        self.use_async = kwargs.get('use_async', False)

        sync_auth_class = SyncBasicAuth if self.is_ssl else OAuth
        self.sync_auth = sync_auth_class(**kwargs)
        self.async_auth = None

        if self.use_async:
            async_auth_class = AsyncBasicAuth if self.is_ssl else OAuth
            self.async_auth = async_auth_class(**kwargs)

    def _is_ssl(self):
        """ Check if url use HTTPS """
        return self.url.startswith("https")

    def _get_url(self, endpoint):
        """ Get URL for requests """
        url = self.url
        api = 'wc-api'

        if url.endswith('/') is False:
            url = f'{url}/'

        if self.wp_api:
            api = 'wp-json'

        return f'{url}{api}/{self.version}/{endpoint}'

    def _get_header(self):
        return {
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
        }

    def _request(self, method, endpoint=None, data=None, url=None, **kwargs):
        params = kwargs.pop('params', False) or dict()
        url = url or self._get_url(endpoint)
        url = self.sync_auth.get_auth_url(url, method, params)
        auth = self.sync_auth.get_auth()
        headers = kwargs.pop('headers', False) or self._get_header()

        request_kwargs = dict(
            method=method,
            url=url,
            verify=self.verify_ssl,
            auth=auth or None,
            timeout=self.timeout,
            headers=headers,
            **kwargs,
        )

        data_type = headers.get('Accept', '').split('/')[-1]  # TODO: to improve
        if data and data_type.lower() == 'json':
            request_kwargs['json'] = data
        else:
            request_kwargs['data'] = data

        _logger.info(f'WooCommerce {method}: {url}')
        response = request(**request_kwargs)
        return response

    async def _async_request(self, session, method, endpoint=None, data=None, **kwargs):
        params = kwargs.pop('params', dict())
        url = self._get_url(endpoint)
        url = self.async_auth.get_auth_url(url, method, params)
        auth = self.async_auth.get_auth()
        headers = self._get_header()
        _logger.info(f'WooCommerce {method}: {url}')

        async with session.request(
                method=method,
                url=url,
                ssl=self.verify_ssl,
                auth=auth,
                data=data,
                timeout=1000,
                headers=headers,
                **kwargs) as response:
            text_response = await response.text()
            text_json = await response.json()

            return {
                'status_code': response.status,
                'text': text_response,
                'json': text_json,
            }

    def get(self, endpoint=None, url=None, **kwargs):
        return self._request('GET', endpoint=endpoint, url=url, **kwargs)

    async def aget(self, session, endpoint=None, url=None, **kwargs):
        result = self._async_request(session, 'GET', endpoint, url, **kwargs)
        return result

    def post(self, endpoint, data, **kwargs):
        return self._request('POST', endpoint=endpoint, data=data, **kwargs)

    def put(self, endpoint, data, **kwargs):
        return self._request('PUT', endpoint=endpoint, data=data, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request('DELETE', endpoint, **kwargs)

    def options(self, endpoint, **kwargs):
        return self._request('OPTIONS', endpoint, **kwargs)
