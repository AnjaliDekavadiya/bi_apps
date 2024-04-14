# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        if not self.env.context.get('do_not_include'):
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            if restricted_customer:
                salesperson_domain = [('salesperson_ids', 'in', self.env.user.ids)]
                if not any(arg[0] == 'id' or arg[0] == 'parent_id' for arg in domain):
                    domain += salesperson_domain
        return super(AccountMove, self)._search(domain, offset, limit, order, access_rights_uid)

    def read(self, fields=None, load='_classic_read'):
        invoices = super(AccountMove, self).read(fields=fields, load=load)
        if len(invoices) == 1:
            if self.env.user.has_group("sales_person_customer_access.group_restricted_customer"):
                invoice_restrict_access_config = self.env['account.move'].sudo().search([('salesperson_ids', 'in', self.env.user.ids)])
                if invoice_restrict_access_config:
                    for invoice in invoices:
                        if invoice.get('id') and invoice.get('id') not in invoice_restrict_access_config.ids:
                            raise AccessError(_("You don't have the access!"))
        return invoices


    salesperson_ids = fields.Many2many(
        'res.users',
        string="Salespersons"
    )
