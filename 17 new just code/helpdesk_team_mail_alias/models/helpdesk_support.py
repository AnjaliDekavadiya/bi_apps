# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    @api.model
    def get_empty_list_help(self, help):
        self = self.with_context(
            empty_list_help_document_name=_("Helpdesk Ticket"),
        )
        return super(
            HelpdeskSupport, self
        ).get_empty_list_help(help)
