#  See LICENSE file for full copyright and licensing details.

from .woocommerce_api import WooCommerceAPI
from .woocommerce_client import WooCommerceClient


class WordPressClient(WooCommerceClient):
    @staticmethod
    def _build_api_client(settings, **kwargs):
        client = WooCommerceAPI(
            url=settings['fields']['url']['value'],
            wp_user=settings['fields']['wp_user']['value'],
            wp_app_password=settings['fields']['wp_app_password']['value'],
            version=settings['fields']['wp_api_version']['value'],
            verify_ssl=settings['fields']['verify_ssl']['value'],
            use_async=settings.get('use_async', False),
            timeout=30,
            **kwargs,
        )
        return client
