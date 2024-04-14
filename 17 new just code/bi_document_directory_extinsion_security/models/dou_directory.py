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


class Directorie_Document(models.Model):
    _inherit = "directorie.document"

    user_ids = fields.Many2many("res.users", string="Users")
    tags_ids = fields.Many2many("document.managemenet.directory", string="Tags")

    @api.onchange("user_ids")
    def set_user(self):
        attachments_env = self.env["ir.attachment"].search([])
        list_attach = []
        for attach in attachments_env:
            for i in self:
                if i.model.model == attach.res_model:
                    users = i.user_ids
                    for k in users:
                        list_attach.append(k.ids[0])
                    attach.write({'user_ids': [(6, 0, list_attach)]})

    @api.onchange("tags_ids")
    def set_tag(self):
        attachments_env = self.env["ir.attachment"].search([])
        list_tags = []
        for attach in attachments_env:
            for i in self:
                if i.model.model == attach.res_model:
                    tags = i.tags_ids
                    for tag in tags:
                        list_tags.append(tag.ids[0])
                    attach.write({'directory_tag_ids': [(6, 0, list_tags)]})


class Document_Managenet_Directory(models.Model):
    _name = "document.managemenet.directory"

    name = fields.Char("Name")


class Document_Managenet_Document(models.Model):
    _name = "document.managemenet.document"

    name = fields.Char("Name")


class Ir_Attachment(models.Model):
    _inherit = "ir.attachment"

    directory_tag_ids = fields.Many2many("document.managemenet.directory", string="Directory tags",
                                         related="directory_id.tags_ids")
    user_ids = fields.Many2many("res.users", string="users", related="directory_id.user_ids")
    attachment_tags_ids = fields.Many2many("document.managemenet.document", string="Attachment tags")
