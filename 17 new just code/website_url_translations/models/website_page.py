#coding: utf-8

from odoo import fields, models


class website_page(models.Model):
    """
    Overwrite to add translations for urls
    """
    _inherit = "website.page"

    url_translation_ids = fields.One2many("page.url.translation", "page_id", string="URL Translitirations")
    sitemap_t_add = fields.Boolean("Add transliterations to sitemap")
