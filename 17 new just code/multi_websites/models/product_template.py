from odoo.http import request

from odoo import api, fields, models
from odoo.exceptions import ValidationError, RedirectWarning, UserError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_ids = fields.Many2many(comodel_name="website", string="Allowed Websites")

    def check_website_accessibility(self):
        self.ensure_one()
        if len(self.website_ids) == 0:
            return True
        if request.website.id in self.website_ids.ids:
            return True
        return False
