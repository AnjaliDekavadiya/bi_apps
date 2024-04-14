# -*- coding: utf-8 -*-
################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
################################################################################
from odoo import http
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.google_shop.controllers.controllers import Google

class MarketplaceGoogle(Google):
    @http.route(['/google/<int:sequence_no>/OAuth2','/<string:url_handler>/google/<int:sequence_no>/OAuth2'], type="http", auth="public", csrf=False, website=True)
    def oauth2_verify(self,sequence_no, **kw):
        return super(MarketplaceGoogle,self).oauth2_verify(sequence_no,**kw)

    @http.route(['/r/<string:html_file>','/r/<string:url_handler>/<string:html_file>'], type="http", auth="public", csrf=False, website=True)
    def website_verify(self, html_file, **kw):
        return super(MarketplaceGoogle, self).website_verify(html_file, **kw)
