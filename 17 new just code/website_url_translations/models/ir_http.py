#coding: utf-8

from odoo import models
from odoo.http import request


class ir_http(models.AbstractModel):
    """
    Re-write to manage translated values
    """
    _inherit = "ir.http"

    @classmethod
    def _serve_page(cls):
        """
        Overwrite to search translated URLs

        Extra info:
         * Here we do not search for ilike pages, since translation is considered as more important
         * We also do not search ilike translations since uniqueness assumes that those are different addresses
        """
        req_page = request.httprequest.path
        website_domain = request.website.website_domain()
        page_domain = [("url", "=", req_page)] + website_domain
        page = request.env["website.page"].sudo().search(page_domain, order="website_id asc", limit=1)
        lang = request.context.get("lang")
        if page:
            translations = request.env["page.url.translation"].sudo().search(
                [("id", "in", page.url_translation_ids and page.url_translation_ids.ids or [])] + website_domain,
                order="website_id asc",
            )
        else:
            translations = request.env["page.url.translation"].sudo().search(
                [("translation", "=", req_page)] + website_domain, order="website_id asc",
            )
        target_url = req_page
        target_page = page
        if translations:
            this_lang_translations = translations.filtered(lambda trans: trans.lang == lang)
            if this_lang_translations:
                target_page = this_lang_translations.page_id
                target_url = this_lang_translations[0].translation
            else:
                target_page = translations[0].page_id
                target_url = target_page.url
        if target_url == req_page:
            request.httprequest.path = target_page.url or req_page
            res = super(ir_http, cls)._serve_page()
        else:
            res = request.redirect(target_url, code=302)
        return res
