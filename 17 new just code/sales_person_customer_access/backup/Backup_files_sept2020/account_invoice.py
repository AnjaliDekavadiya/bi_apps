# -*- coding: utf-8 -*-

# from openerp import models, fields, api
from odoo import models, fields, api


class AccountMove(models.Model):
    # _inherit = "account.invoice" #odoo13
    _inherit = "account.move"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
        if restricted_customer:
            args = [('salesperson_ids','in',self.env.user.id)] + list(args)
        return super(AccountMove, self)._search(args, offset, limit, order, count, access_rights_uid)

    salesperson_ids = fields.Many2many(
        'res.users',
        string="Salespersons"
    )
