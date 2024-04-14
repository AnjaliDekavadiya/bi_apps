# See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError


class WooCommerceApiException(UserError):
    def __init__(self, message, error_code):
        super().__init__(message)

        self.error_code = error_code
