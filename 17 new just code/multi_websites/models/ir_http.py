# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo.http import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.http_routing.models.ir_http import ModelConverter

import logging
_logger = logging.getLogger(__name__)


class ModelConverterMW(ModelConverter):

    def generate(self, uid, dom=None, args=None):
        Model = request.env[self.model].with_user(uid)
        # Allow to current_website_id directly in route domain
        args.update(current_website_id=request.env['website'].get_current_website().id)
        domain = safe_eval(self.domain, (args or {}).copy())
        if dom:
            domain += dom
        if self.model == 'product.template':
            product_tmpl_ids = request.env['website'].get_current_website().product_tmpl_ids.ids
            domain += ['|',('website_ids','=',False),('id','in',product_tmpl_ids)]
        for record in Model.search(domain):
            # return record so URL will be the real endpoint URL as the record will go through `slug()`
            # the same way as endpoint URL is retrieved during dispatch (301 redirect), see `to_url()` from ModelConverter
            yield record


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_converters(cls):
        return dict(
            super(IrHttp, cls)._get_converters(),
            model=ModelConverterMW,
        )


