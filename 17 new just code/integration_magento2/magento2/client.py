# See LICENSE file for full copyright and licensing details.
import logging
import requests

from odoo import _

from .exceptions import Magento2ApiException


_logger = logging.getLogger(__name__)


class Client:

    def __init__(self, host, access_token, shop_ids, store_view_code=None, locale=None):
        self.host = host
        self.access_token = access_token
        self.shop_ids = shop_ids
        self.store_view_code = store_view_code
        self.locale = locale
        self._all_stores = self.get('store/storeConfigs')
        self._store_weight_uom = None

    def _store(self):
        code = self.store_view_code
        stores = self._stores_active()
        store_default = stores[0]
        if not code:
            return store_default

        for store_ in stores:
            if store_['code'] == code:
                return store_

        return store_default

    def _stores_active(self):
        all_stores = self._all_stores
        shop_ids_config = self.shop_ids

        if not shop_ids_config:
            return all_stores

        active_stores = list()
        all_stores_dict = {x['id']: x for x in all_stores}
        shop_ids = [int(x) for x in shop_ids_config.split(',')]

        for store_id in shop_ids:
            if store_id not in all_stores_dict:
                raise Exception(_(
                    'Settings `shop_ids`: invalid store identifier "%s".' % store_id
                ))
            active_stores.append(all_stores_dict[store_id])

        return active_stores

    def _lang(self):
        if self.locale:
            return self.locale

        store = self._store()
        return store['locale'].split('_')[0].lower()

    @property
    def store_weight_uom(self):
        if not self._store_weight_uom:
            store = self._store()
            self._store_weight_uom = store['weight_unit']

        return self._store_weight_uom

    def _with_store_view(self, code, locale):
        store_view_client = self.__class__(
            self.host,
            self.access_token,
            self.shop_ids,
            store_view_code=code,
            locale=locale,
        )
        return store_view_client

    def get(self, url, domain=None, **kw):
        params = self._convert_domain_to_params(domain)
        params.update(kw)
        result = self._send_request('GET', url, params=params)
        return result

    def post(self, url, data=None):
        result = self._send_request('POST', url, data=data)
        return result

    def put(self, url, data=None):
        result = self._send_request('PUT', url, data=data)
        return result

    def delete(self, url):
        result = self._send_request('DELETE', url)
        return result

    def _convert_domain_to_params(self, domain):
        params = {}

        if domain is None:
            return params
        elif not domain:
            params['search_criteria'] = ''
            return params

        field_names = ('field', 'condition_type', 'value')

        for group_num, domain_tuple in enumerate(domain):
            for field, value in zip(field_names, domain_tuple):
                key = (
                    f'search_criteria[filter_groups][{group_num}][filters][0][{field}]'
                )
                params[key] = value

        return params

    def _send_request(self, method, url, *, params=None, data=None):
        url = self._build_url(url)
        headers = self._build_headers()
        _logger.debug('%s %s %s %s', method, url, params, data)

        response = requests.request(
            method,
            url,
            params=params,
            json=data,
            headers=headers,
        )

        self._check_response(response)

        result = response.json()
        return result

    def _build_url(self, url):
        store_view_code = f'/{self.store_view_code}' if self.store_view_code else ''
        return f'{self.host}/rest{store_view_code}/V1/{url}'

    def _build_headers(self):
        headers = {
            'User-Agent': 'VentorTech-Odoo-Magento2-Connector-PRO/1.X',
            'Authorization': f'Bearer {self.access_token}',
        }
        return headers

    def _check_response(self, response):
        if not response.ok:
            raise Magento2ApiException(response.text)

    def _fetch_one(self, url, code):
        domain = [('entity_id', 'eq', code)]
        result = self.get(url, domain=domain)
        if isinstance(result, dict) and 'items' in result and not result['items']:
            result['items'] = list()
        return result['items'][0] if result['items'] else dict()
