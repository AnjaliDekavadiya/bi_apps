# -*- coding: utf-8 -*-
from .template import get_all_font_list, rchop, remove_font_prefix_num
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    @staticmethod
    def get_template_report_font_assets():
        body = ""
        for each in get_all_font_list(with_extension=True):
            body += """@font-face {font-family: '%s'; src: URL('/report_utils/static/fonts/%s') format('truetype');}
            """ % (remove_font_prefix_num(rchop(each[0], ".ttf")), each[0])
        return "<style>%s</style>" % body


