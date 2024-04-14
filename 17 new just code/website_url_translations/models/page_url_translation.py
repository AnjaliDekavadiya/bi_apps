#coding: utf-8

from odoo import _, api, fields, models

from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.base.models.res_partner import _lang_get


class page_url_translation(models.Model):
    """
    Overwrite to add translations for urls
    """
    _name = "page.url.translation"
    _description = "URL Translitiration"
    _rec_name = "translation"

    @api.onchange("translation")
    def _onchange_translation(self):
        """
        Onchange method for translation
        """
        for translation in self:
            translation_decoded = "/" + slugify(translation.translation, max_length=1024, path=True)
            if translation.translation != translation_decoded:
                translation.translation = translation_decoded

    page_id = fields.Many2one("website.page", string="Page", ondelete="cascade")
    lang = fields.Selection(_lang_get, string="Language", default=lambda self: self.env.user.lang, required=True)
    translation = fields.Char(string="Translitiration", required=True)
    website_id = fields.Many2one(related="page_id.view_id.website_id", store=True, readonly=False, ondelete="cascade")

    _sql_constraints = [
        (
            "unique_translation_per_page",
            "unique(page_id,lang)",
            _("There might only one URL Translitiration for the same page!")
        ),
        (
            "unique_trasnlation_per_language",
            "unique(lang,translation)",
            _("URL Translitiration should be unique within one language!")
        ),
    ]
