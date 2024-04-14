# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def get_views(self, views, options=None):
        res = super(AccountMove, self).get_views(views=views, options=options)
        if res.get("views", False) and res.get("views").get("list", False) and res.get("views").get("list").get("id", False):
            view = self.env["ir.ui.view"].browse([res["views"]["list"]["id"]])
            if self.env.ref("account.view_out_invoice_tree").id != view.id:
                form_toolbar = res['views']['form']['toolbar'] if 'form' in res['views'] else {}
                for action in form_toolbar.get('action', []):
                    if action.get('name') == 'Make Recurring':
                        form_toolbar.get('action').remove(action)
                        break
        return res
