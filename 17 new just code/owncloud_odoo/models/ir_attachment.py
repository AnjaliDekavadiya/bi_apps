# -*- coding: utf-8 -*-

from odoo import fields, models


class ir_attachment(models.Model):
    """
    Re-writting to keep path in addition to key
    """
    _inherit = "ir.attachment"

    owncloud_path = fields.Char(string="ownCloud/Nextcloud path")
