# -*- coding: utf-8 -*-

# from openerp import models, fields, api
from odoo import models, fields, api , _
from odoo.exceptions import AccessError, MissingError


class AccountMove(models.Model):
    # _inherit = "account.invoice" #odoo13
    _inherit = "account.move"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self.env.context.get('do_not_include'):
            pass
        else:
            restricted_customer = self.env.user.has_group('sales_person_customer_access.group_restricted_customer')
            if restricted_customer:
                args = [('salesperson_ids','in',self.env.user.ids)] + list(args)
        return super(AccountMove, self)._search(args, offset, limit, order, count, access_rights_uid)

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
