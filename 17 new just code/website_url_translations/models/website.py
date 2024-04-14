#coding: utf-8

from itertools import chain

from odoo import fields, models


class Website(models.Model):
    """
    Overwrite to properly enumerate pages for sitemap
    """
    _inherit = "website"

    def _enumerate_pages(self, query_string=None, force=False):
        """
        Overwrite to add transliterated URLs to sitemap
        """
        res = super(Website, self)._enumerate_pages(query_string=query_string, force=force)
        res = [loc for loc in res]
        domain = []
        if not force:
            domain += [("website_indexed", "=", True), ("visibility", "=", False), ("sitemap_t_add", "=", True)]
            domain += [
                ("website_published", "=", True), ("visibility", "=", False),
                "|", ("date_publish", "=", False), ("date_publish", "<=", fields.Datetime.now())
            ]
        if query_string:
            domain += [("url", "like", query_string)]
        pages = self._get_website_pages(domain)
        trans_pages = []
        for page in pages:
            for transl in page.sudo().url_translation_ids:
                trans_pages.append({
                    "loc": "/{}{}".format(
                        self.env["res.lang"].sudo()._lang_get(transl.lang).url_code,transl.translation,
                    ),
                    "name": transl.page_id.name,
                    "lastmod": fields.Date.to_string(transl.write_date.date()),
                })
        res = chain(res, trans_pages)
        return res
