# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import uuid

from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class DirectoriesPortal(models.Model):
	_inherit = "ir.attachment"

	user_id = fields.Many2many('res.users','ir_attachment_rel', 'attachment_id', 'user_id',string="Share on portal")
