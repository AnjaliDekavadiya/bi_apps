#  See LICENSE file for full copyright and licensing details.

import asyncio
from copy import deepcopy

from odoo.addons.integration.tools import make_list_if_not

try:
    import aiohttp
except (ImportError, IOError) as ex:
    import logging
    _logger = logging.getLogger(__name__)
    _logger.error(ex)

from .exceptions import WooCommerceApiException
from .woocommerce_api import WooCommerceAPI

# WooCommerce restrictions
MAX_BATCH_SIZE = 100
MAX_PAGE_SIZE = 100


class WooCommerceClient:
    def __init__(self, settings, **kwargs):
        self._client = self._build_api_client(settings, **kwargs)
        self.use_async = settings.get('use_async', False)

    @staticmethod
    def _build_api_client(settings, **kwargs):
        client = WooCommerceAPI(
            url=settings['fields']['url']['value'],
            consumer_key=settings['fields']['consumer_key']['value'],
            consumer_secret=settings['fields']['consumer_secret']['value'],
            version=settings['fields']['wc_api_version']['value'],
            verify_ssl=settings['fields']['verify_ssl']['value'],
            use_async=settings.get('use_async', False),
            timeout=30,
            **kwargs,
        )
        return client

    def fetch_one(self, endpoint, params=None):
        response = self._client.get(endpoint, params=params)

        if response.status_code == 404:
            return dict()

        self.check_response(response)

        return response.json()

    def get(self, endpoint, page=1, limit=0, **kwargs):
        page = page or 1

        if 'params' not in kwargs:
            kwargs['params'] = {}

        if 'per_page' not in kwargs['params']:
            kwargs['params']['per_page'] = MAX_PAGE_SIZE

        if self.use_async:
            result = self.get_by_async(endpoint, page, limit, **kwargs)
        else:
            result = self.get_by_pages(endpoint, page, limit, **kwargs)

        return result[:limit] if limit else result

    def get_by_pages(self, endpoint, page=1, limit=0, **kwargs):
        result = []
        next_link = True

        while next_link:
            kwargs['params'].update({'page': page})
            response = self._client.get(endpoint, **kwargs)
            self.check_response(response)

            result += make_list_if_not(response.json())
            page += 1
            next_link = response.links.get('next')

            if limit and len(result) >= limit:
                break

        return result

    def get_by_async(self, endpoint, page=1, limit=0, **kwargs):
        kwargs['params'].update({'page': page})

        response = self._client.get(endpoint, **kwargs)
        self.check_response(response)

        pages_count = int(response.headers.get('X-WP-TotalPages', page))

        if limit:
            pages_count = page + limit / MAX_PAGE_SIZE - 1

        result = make_list_if_not(response.json())

        if pages_count > page:
            coroutines = self.create_coroutines(page + 1, pages_count, endpoint, kwargs)
            rest_tasks = asyncio.run(coroutines)

            for res in rest_tasks:
                self.async_check_response(res)
                result.extend(make_list_if_not(res['json']))

        return result

    async def create_coroutines(self, first_page, pages_count, endpoint, kwargs):
        tasks = list()

        async with aiohttp.ClientSession() as session:
            for page in range(first_page, pages_count + 1):
                kwargs = deepcopy(kwargs)
                kwargs['params'].update({'page': page})
                task = await self._client.aget(session, endpoint, **kwargs)
                tasks.append(task)

            values = await asyncio.gather(*tasks)
            return values

    @staticmethod
    def check_response(response):
        if response.status_code not in (200, 201):
            raise WooCommerceApiException(response.text, response.status_code)

    @staticmethod
    def async_check_response(response):
        if response['status_code'] not in (200, 201):
            raise WooCommerceApiException(response['text'], response['status_code'])

    def get_by_direct_link(self, link_url):
        response = self._client.get(url=link_url)
        self.check_response(response)
        return response.content

    def create_obj(self, endpoint, data, **kwargs):
        response = self._client.post(endpoint, data, **kwargs)
        self.check_response(response)
        return response.json()

    def update(self, endpoint, data, **kwargs):
        response = self._client.put(endpoint, data, **kwargs)
        self.check_response(response)
        return response.json()

    def delete(self, endpoint, **kwargs):
        response = self._client.delete(endpoint, **kwargs)
        self.check_response(response)
        return response.json()

    def post_batch_operations(self, operation, endpoint, data, **kwargs):
        result = list()

        while data:
            response = self._client.post(
                endpoint + '/batch', {operation: data[:MAX_BATCH_SIZE]}, **kwargs)
            self.check_response(response)
            response_json = response.json()
            result.extend(response_json[operation])
            data = data[MAX_BATCH_SIZE:]

        return result

    def update_batch(self, endpoint, data, **kwargs):
        response = self.post_batch_operations('update', endpoint, data, **kwargs)
        return response

    def delete_batch(self, endpoint, data, **kwargs):
        response = self.post_batch_operations('delete', endpoint, data, **kwargs)
        return response
